from cryptography.fernet import Fernet
import json
import os
import base64
import hashlib
from infrastructure.objects.application import Application
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


class ApplicationManager:
    save_path = "data/applications"

    def __init__(self, key):
        self.fernet = Fernet(key)

        if not os.path.exists("/info"):
            with open(f"{ApplicationManager.save_path}/info", "wb") as file:
                file.write(
                    zlib.compress(
                        self.fernet.encrypt(
                            b'{"password": "'
                            + key
                            + b'", "lastid": 0, "names": {}, "publishers": {}, "developers": {} }'
                        )
                    )
                )

        with open(f"{ApplicationManager.save_path}/info", "rb") as file:
            read = zlib.decompress(file.read())

        decrypted = self.fernet.decrypt(read)

        self.data = json.loads(decrypted)

        self._changes = []

    def save(self):
        with open(f"{ApplicationManager.save_path}/info", "wb") as file:
            file.write(
                zlib.compress(self.fernet.encrypt(json.dumps(self.data).encode()))
            )

    def add_application(self, app: Application) -> int:
        self.data["lastid"] += 1
        app.id = self.data["lastid"]

        if not self.publisher_exists(app.publisherid):
            self.data["publishers"][app.publisherid] = []
        if not self.developer_exists(app.developerid):
            self.data["developers"][app.developerid] = []

        self.data["publishers"][app.publisherid].append(app.id)
        self.data["developers"][app.developerid] = app.id
        a = app.__dict__
        with open(f'{ApplicationManager.save_path}/{self.data["lastid"]}', "wb") as f:
            f.write(zlib.compress(self.fernet.encrypt(json.dumps(a).encode())))
        self.save()

        return self.data["lastid"]

    def id_exists(self, id: int):
        return self.data["lastid"] >= id and id > 0

    def publisher_exists(self, publisherid: int):
        return self.data["publishers"].__contains__(publisherid)

    def developer_exists(self, developerid: int):
        return self.data["developers"].__contains__(developerid)

    def get_application_by_id(self, id: int):
        with open(f"{ApplicationManager.save_path}/" + str(id), "rb") as f:
            data = json.loads(self.fernet.decrypt(zlib.decompress(f.read())).decode())
        return Application.from_dict(data)

    def get_applications_by_publisher(self, publisherid: int):
        if not self.publisher_exists(publisherid):
            return None
        return [
            self.get_application_by_id(id)
            for id in self.data["publishers"][publisherid]
        ]

    def get_applications_by_developer(self, developerid: int):
        if not self.developer_exists(developerid):
            return None
        return [
            self.get_application_by_id(id)
            for id in self.data["developers"][developerid]
        ]


if __name__ == "__main__":
    try:
        am = ApplicationManager(load_key())
    except:
        write_key()
        am = ApplicationManager(load_key())

    for i in range(1000):
        id = am.add_application(
            Application(
                "0x01010",
                "Ömer Faruk Nehir",
                "omerfaruknehir@gmail.com",
                "0x01010",
                "05519454322",
            )
        )
        print(am.check_password_by_id(id, "0x01010"))
