import json
import os
from functools import wraps
from infrastructure.decorators import type_check


class _Secrets:
    secrets_file = "app"
    static_secrets = True
    secrets_from_root = True
    __secrets = {}

    def __load_secrets():
        directory = ""
        props = {}

        if _Secrets.secrets_from_root:
            for dir in ["/"] + os.getcwd().split(os.pathsep):
                directory = os.path.join(directory, dir)
                if os.path.exists(os.path.join(directory, ".secrets")):
                    try:
                        props.update(
                            json.load(
                                open(
                                    os.path.join(directory, ".secrets"),
                                    "r",
                                    encoding="utf8",
                                )
                            )
                        )
                    except json.JSONDecodeError:
                        pass

        if os.path.exists(
            os.path.join(os.getcwd(), _Secrets.secrets_file + ".secrets")
        ):
            props.update(
                json.load(
                    open(
                        os.path.join(os.getcwd(), _Secrets.secrets_file + ".secrets"),
                        "r",
                        encoding="utf8",
                    )
                )
            )

        return props

    @classmethod
    def load_secrets(cls):
        _Secrets.__secrets = _Secrets.__load_secrets()

    @property
    def secrets(self) -> dict[str, object]:
        if _Secrets.static_secrets:
            if _Secrets.__secrets is None:
                raise ValueError(
                    "Please load secrets or set static_secrets as False to load secrets dynamically on evert call of secrets"
                )
            else:
                return _Secrets.__secrets
        else:
            return _Secrets.__load_secrets()

    @secrets.setter
    @type_check
    def secrets(self, any):
        raise ValueError("You cannot set secrets :(")

    @classmethod
    def get(cls, key):
        return cls.secrets.fget(cls).get(key)


Secrets = _Secrets()
