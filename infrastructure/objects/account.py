import hashlib
import pyargon2
from infrastructure.objects.developer import Developer
from infrastructure.objects.publisher import Publisher
import os
from superstructure.properties import Properties


class Account:
    prime_keys = {"username": False, "email": False}
    salt = Properties.get("HASH_SALT")

    def __init__(
        self,
        username: str,
        name: str,
        email: str,
        password: str,
        date_created: str,
        phone_number: str = "",
        sessions: list = [],
        library: list = [],
        removed: bool = False,
        developer: Developer | None = None,
        publisher: Publisher | None = None,
        id=None,
    ):
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.date_created = date_created
        self.phone_number = phone_number
        self.sessions = sessions
        self.library = library
        self.removed = removed
        self.developer = developer
        self.publisher = publisher

    @staticmethod
    def from_dict(dict: dict):
        return Account(
            dict["username"],
            dict["name"],
            dict["email"],
            dict["password"],
            dict["date_created"],
            dict["phone_number"],
            dict["sessions"],
            dict["library"],
            dict["removed"],
            dict["developer"],
            dict["publisher"],
            dict["id"],
        )

        # TODO: remove this code
        self.id = dict["id"]
        self.username = dict["username"]
        self.name = dict["name"]
        self.email = dict["email"]
        self.password = dict["password"]
        self.phone_number = dict["phone_number"]
        self.library = dict["library"]
        self.removed = dict["removed"]
        # TODO end

    @staticmethod
    def hash_password(password, salt=None) -> str|bytes|None:
        """
        `password`: The password to hash it.

        `salt`: Salt of `argon2id`, default is `Account.salt`
        """
        if salt is None:
            salt = Account.salt
            if (
                salt is # still
                None
                ):
                raise Exception("This is a SECURITY ERROR: salt (for password hashing) is `None`!")
        return pyargon2.hash(password, salt=salt)

    def check_password(self, password, salt=None) -> bool|int:
        """
        Compare the input `password` with `account.password` by hashing the password and returning if they are same.
            (Because `account.password` is hashed already)

        `password`: The password to compare it.

        `salt`: Salt of `argon2id`, default is `Account.salt`
        """
        if salt is None:
            salt = Account.salt
            if (
                salt is # still
                None
                ):
                raise Exception("This is a SECURITY ERROR: salt (for password hashing) is `None`!")
        try:
            return pyargon2.hash(password, salt=salt) == self.password
        except:
            # Support legacy hash algorithms to prevent users from
            # resetting  their  passwords. (Also, I wrote this now
            # just to avoid  writing  it down if I change the hash
            # algorithm in the future, it is of no use right now.)
            try:
                res = (
                    hashlib.md5(str.encode(password), usedforsecurity=True).hexdigest()
                    == self.password
                )
                if res:
                    self.password = password
                    return 2
                else:
                    return False
            except:
                return False
