from cryptography.fernet import Fernet
import json
import os
import pyargon2
from infrastructure.objects.account import Account
from infrastructure.decorators import type_check
import zlib
import inspect

UNDEFINED = object()

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

class DataManager:
    @type_check
    def __init__(self, data_type, data_name: str, key: bytes, salt: str):
        self.fernet = Fernet(key)
        self.salt = salt
        self.save_path = os.path.join("data", data_name)
        self.data_type = data_type
        mro = data_type.mro()

        static_variable_value = getattr(mro[0], "prime_keys", None)
        init_signature = inspect.signature(data_type.__init__)
        # Get the parameters, their default values, and types (if any)
        self.params = {
            name: {
                'default': param.default if param.default is not param.empty else UNDEFINED,
                'type': param.annotation if param.annotation is not param.empty else UNDEFINED
            }
            for name, param in init_signature.parameters.items()
        }

        print(self.params)

        if not os.path.exists(f"{self.save_path}/info"):
            self.data = {"password": key, "lastid": 0, "emails": {}, "usernames": {}}
            self.save()

        with open(f"{self.save_path}/info", "rb") as file:
            read = zlib.decompress(file.read())

        decrypted = self.fernet.decrypt(read)

        self.data = json.loads(decrypted)

        self._changes = []

    def save(self):
        with open(f"{self.save_path}/info", "wb") as file:
            file.write(
                zlib.compress(self.fernet.encrypt(json.dumps(self.data).encode()))
            )

    @type_check
    def hash_password(self, password: str) -> str|bytes|None:
        return pyargon2.hash(
            password,
            salt=self.salt
        )

    @type_check
    def add_account(self, account: Account) -> int:
        self.data["lastid"] += 1
        account.id = self.data["lastid"]
        self.data["emails"][account.email] = account.id
        self.data["usernames"][account.username] = account.id
        a = account.__dict__
        a["password"] = self.hash_password(a["password"])
        with open(f'{self.save_path}/{self.data["lastid"]}', "wb") as f:
            f.write(zlib.compress(self.fernet.encrypt(json.dumps(a).encode())))
        self.save()

        return self.data["lastid"]
    
    @type_check
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
        with open(f'{self.save_path}/{account.id}', "wb") as f:
            f.write(zlib.compress(self.fernet.encrypt(json.dumps(a).encode())))
        self.save()

        return 4

    @type_check
    def id_exists(self, id: int) -> bool:
        return self.data["lastid"] >= id and id > 0

    @type_check
    def username_exists(self, username: str) -> bool:
        return self.data["usernames"].__contains__(username)

    def email_exists(self, email: str) -> bool:
        return self.data["emails"].__contains__(email)

    def get_account_by_id(self, id: int) -> Account|None:
        if not os.path.exists(f"{self.save_path}/" + str(id)):
            return None
        with open(f"{self.save_path}/" + str(id), "rb") as f:
            data = json.loads(self.fernet.decrypt(zlib.decompress(f.read())).decode())
        return Account.from_dict(data)

    def get_account_by_username(self, username: str) -> Account|None:
        return self.get_account_by_id(self.data["usernames"].get(username))

    def get_account_by_email(self, email: str) -> Account|None:
        return self.get_account_by_id(self.data["emails"].get(email))

    def check_password_by_id(self, id: int, password: str) -> bool:
        res = self.get_account_by_id(id).check_password(password, self.salt)
        if res == 2: # Password update required due to hashing algorithm update.
            res = True
            account = self.get_account_by_id(id)
            if account == None:
                raise ValueError("Account is None (But it shouldn't be None!)")
            account.password = self.hash_password(password)
            self.update_account(account)
        return res

    def check_password_by_email(self, email: str, password: str) -> bool:
        return self.check_password_by_id(self.data["emails"].get(email), password)

    def check_password_by_username(self, username: str, password: str) -> bool:
        return self.check_password_by_id(self.data["usernames"].get(username), password)


# if __name__ == "__main__":
#     try:
#         am = DataManager(load_key())
#     except:
#         write_key()
#         am = DataManager(load_key())
# 
#     for i in range(1000):
#         id = am.add_account(
#             Account(
#                 "0x01010",
#                 "Ömer Faruk Nehir",
#                 "omerfaruknehir@gmail.com",
#                 "0x01010",
#                 "only a phone number",
#             )
#         )
#         print(am.check_password_by_id(id, "0x01010"))