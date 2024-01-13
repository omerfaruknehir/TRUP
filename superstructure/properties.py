import json
import os
from functools import wraps
from infrastructure.decorators import type_check


class _Properties:
    properties_file = "app"
    static_properties = True
    properties_from_root = True
    __properties = {}

    def __load_properties():
        directory = ""
        props = {}

        if _Properties.properties_from_root:
            for dir in ["/"] + os.getcwd().split(os.pathsep):
                directory = os.path.join(directory, dir)
                if os.path.exists(os.path.join(directory, ".properties")):
                    try:
                        props.update(
                            json.load(
                                open(
                                    os.path.join(directory, ".properties"),
                                    "r",
                                    encoding="utf8",
                                )
                            )
                        )
                    except json.JSONDecodeError:
                        pass

        if os.path.exists(
            os.path.join(os.getcwd(), _Properties.properties_file + ".properties")
        ):
            props.update(
                json.load(
                    open(
                        os.path.join(
                            os.getcwd(), _Properties.properties_file + ".properties"
                        ),
                        "r",
                        encoding="utf8",
                    )
                )
            )

        return props

    @classmethod
    def load_properties(cls):
        _Properties.__properties = _Properties.__load_properties()

    @property
    def properties(self) -> dict[str, object]:
        if _Properties.static_properties:
            if _Properties.__properties is None:
                raise ValueError(
                    "Please load properties or set static_properties as False to load properties dynamically on evert call of properties"
                )
            else:
                return _Properties.__properties
        else:
            return _Properties.__load_properties()

    @properties.setter
    @type_check
    def properties(self, any):
        raise ValueError("You cannot set properties :(")

    @classmethod
    def get(cls, key):
        return cls.properties.fget(cls).get(key)


Properties = _Properties()
