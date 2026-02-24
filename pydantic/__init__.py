from __future__ import annotations

import json
import types
from datetime import datetime
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints


class ValidationError(ValueError):
    pass


class FieldInfo:
    def __init__(self, default: Any = ..., **constraints: Any) -> None:
        self.default = default
        self.constraints = constraints
        self.default_factory = constraints.get("default_factory")


def Field(default: Any = ..., **constraints: Any) -> FieldInfo:
    return FieldInfo(default=default, **constraints)


def field_validator(*field_names: str):
    def decorator(func):
        func.__field_validator_for__ = field_names
        return func

    return decorator


class BaseModel:
    __field_defaults__: dict[str, Any]
    __field_constraints__: dict[str, dict[str, Any]]
    __field_validators__: dict[str, list[Any]]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.__field_defaults__ = {}
        cls.__field_constraints__ = {}
        cls.__field_validators__ = {}
        cls.__resolved_annotations__ = {k: v for k, v in get_type_hints(cls).items() if not k.startswith("__")}
        for name in cls.__resolved_annotations__:
            attr = getattr(cls, name, ...)
            if isinstance(attr, FieldInfo):
                if attr.default_factory is not None:
                    cls.__field_defaults__[name] = attr.default_factory
                else:
                    cls.__field_defaults__[name] = attr.default
                cls.__field_constraints__[name] = {k: v for k, v in attr.constraints.items() if k != "default_factory"}
            elif attr is not ...:
                cls.__field_defaults__[name] = attr
                cls.__field_constraints__[name] = {}
            else:
                cls.__field_constraints__[name] = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "__field_validator_for__"):
                for field in attr.__field_validator_for__:
                    cls.__field_validators__.setdefault(field, []).append(attr)

    def __init__(self, **kwargs: Any) -> None:
        for name, typ in self.__resolved_annotations__.items():
            if name in kwargs:
                value = kwargs[name]
            else:
                default = self.__field_defaults__.get(name, ...)
                if default is ...:
                    raise ValidationError(f"Missing required field: {name}")
                value = default() if callable(default) and not isinstance(default, type) else default

            parsed = self._coerce_type(name, value, typ)
            parsed = self._apply_constraints(name, parsed)
            for validator in self.__field_validators__.get(name, []):
                parsed = validator(parsed)
            setattr(self, name, parsed)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]):
        try:
            return cls(**payload)
        except Exception as exc:
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError(str(exc)) from exc

    def model_dump(self) -> dict[str, Any]:
        return {name: self._to_jsonable(getattr(self, name)) for name in self.__resolved_annotations__}

    def model_dump_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent)

    @classmethod
    def _coerce_type(cls, name: str, value: Any, typ: Any) -> Any:
        origin = get_origin(typ)
        args = get_args(typ)

        if origin in (Union, types.UnionType):
            for arg in args:
                if arg is type(None) and value is None:
                    return None
                try:
                    return cls._coerce_type(name, value, arg)
                except ValidationError:
                    continue
            raise ValidationError(f"Invalid type for {name}")

        if origin is Literal:
            if value not in args:
                raise ValidationError(f"Invalid literal for {name}: {value}")
            return value

        if origin is list:
            if not isinstance(value, list):
                raise ValidationError(f"Expected list for {name}")
            inner = args[0] if args else Any
            return [cls._coerce_type(name, item, inner) for item in value]

        if origin is dict:
            if not isinstance(value, dict):
                raise ValidationError(f"Expected dict for {name}")
            return value

        if typ is datetime:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            raise ValidationError(f"Invalid datetime for {name}")

        if isinstance(typ, type) and issubclass(typ, BaseModel):
            if isinstance(value, typ):
                return value
            if isinstance(value, dict):
                return typ.model_validate(value)
            raise ValidationError(f"Invalid object for {name}")

        if typ in (str, float, int):
            try:
                return typ(value)
            except Exception as exc:
                raise ValidationError(f"Invalid {typ.__name__} for {name}") from exc

        return value

    def _apply_constraints(self, name: str, value: Any) -> Any:
        constraints = self.__field_constraints__.get(name, {})
        if value is None:
            return value
        min_length = constraints.get("min_length")
        max_length = constraints.get("max_length")
        ge = constraints.get("ge")
        le = constraints.get("le")

        if min_length is not None and hasattr(value, "__len__") and len(value) < min_length:
            raise ValidationError(f"{name} below min_length")
        if max_length is not None and hasattr(value, "__len__") and len(value) > max_length:
            raise ValidationError(f"{name} above max_length")
        if ge is not None and value < ge:
            raise ValidationError(f"{name} below minimum")
        if le is not None and value > le:
            raise ValidationError(f"{name} above maximum")
        return value

    def _to_jsonable(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        if isinstance(value, datetime):
            return value.isoformat()
        return value
