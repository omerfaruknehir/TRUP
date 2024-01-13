from cryptography.fernet import Fernet
import json
import os
import pyargon2
from infrastructure.objects.account import Account
import zlib


def write_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


class AccountManager:
    save_path = "data/accounts"

    def __init__(self, key: bytes, salt: str):
        self.fernet = Fernet(key)
        self.salt = salt

        if not os.path.exists(f"{AccountManager.save_path}/info"):
            self.data = {"password": key, "lastid": 0, "emails": {}, "usernames": {}}
            self.save()

        with open(f"{AccountManager.save_path}/info", "rb") as file:
            read = zlib.decompress(file.read())

        decrypted = self.fernet.decrypt(read)

        self.data = json.loads(decrypted)

        self._changes = []

    def save(self):
        with open(f"{AccountManager.save_path}/info", "wb") as file:
            file.write(
                zlib.compress(self.fernet.encrypt(json.dumps(self.data).encode()))
            )

    def hash_password(self, password):
        return pyargon2.hash(
            password,
            salt=self.salt
        )

    def add_account(self, account: Account) -> int:
        self.data["lastid"] += 1
        account.id = self.data["lastid"]
        self.data["emails"][account.email] = account.id
        self.data["usernames"][account.username] = account.id
        a = account.__dict__
        a["password"] = self.hash_password(a["password"])
        with open(f'{AccountManager.save_path}/{self.data["lastid"]}', "wb") as f:
            f.write(zlib.compress(self.fernet.encrypt(json.dumps(a).encode())))
        self.save()

        return self.data["lastid"]
    
    def update_account(self, account: Account) -> int:
        if account.id == None:
            raise Exception("Please create this account first!")
        a = account.__dict__
        if self.data["emails"].get(account.email) != None and self.data["emails"][account.email] != account.id:
            return 2
        if self.data["usernames"].get(account.username) != None and self.data["usernames"][account.username] != account.id:
            return 1
        self.data["emails"].pop(self.get_account_by_id(account.id).email)
        self.data["emails"][account.email] = account.id
        self.data["usernames"].pop(self.get_account_by_id(account.id).username)
        self.data["usernames"][account.username] = account.id
        with open(f'{AccountManager.save_path}/{account.id}', "wb") as f:
            f.write(zlib.compress(self.fernet.encrypt(json.dumps(a).encode())))
        self.save()

        return 4

    def id_exists(self, id: int) -> bool:
        return self.data["lastid"] >= id and id > 0

    def username_exists(self, username: str) -> bool:
        return self.data["usernames"].__contains__(username)

    def email_exists(self, email: str) -> bool:
        return self.data["emails"].__contains__(email)

    def get_account_by_id(self, id: int) -> Account|None:
        if not os.path.exists(f"{AccountManager.save_path}/" + str(id)):
            return None
        with open(f"{AccountManager.save_path}/" + str(id), "rb") as f:
            data = json.loads(self.fernet.decrypt(zlib.decompress(f.read())).decode())
        return Account.from_dict(data)

    def get_account_by_username(self, username: str) -> Account|None:
        return self.get_account_by_id(self.data["usernames"].get(username))

    def get_account_by_email(self, email: str) -> Account|None:
        return self.get_account_by_id(self.data["emails"].get(email))
