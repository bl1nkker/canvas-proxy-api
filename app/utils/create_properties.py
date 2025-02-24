from typing import Callable


def json_property(json_field: str, dto_class: Callable):
    @property
    def prop(self):
        json_data = getattr(self, json_field)
        if json_data:
            return dto_class(**json_data)

    return prop


def create_properties(fields: dict[str, Callable]):
    def decorator(cls):
        for field, dto_class in fields.items():
            prop_name = field + "_meta"
            setattr(cls, prop_name, json_property(field, dto_class))
        return cls

    return decorator
