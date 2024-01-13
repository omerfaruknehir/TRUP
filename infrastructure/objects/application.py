# (CTRL+C, CTRL+V) + Some VS Code shortcuts (If you don't know: Select a position on code and click another position while pressing ALT+SHIFT)
# Long live VS Code!
class Application:
    def __init__(
        self,
        name: str,
        publisherid: int,
        developerid: int,
        contact_mail: str = "",
        website: str = "",
        description: str = "",
        icon: bytes = None,
        screenshots: list[bytes] = [],
        faq: list = [],
        comments: list[int] = [],
        rate_score: float = 0,
        rate_number: int = 0,
        price: dict[str, dict[str, float]] = [],
        versions: dict[str, dict[str, str]] = [],
        public: bool = True,
        archived: bool = False,
        removed: bool = False,
        id=None,
    ):
        self.id = id
        self.name = name
        self.publisherid = publisherid
        self.developerid = developerid
        self.contact_mail = contact_mail
        self.website = website
        self.description = description
        self.icon = icon
        self.screenshots = screenshots
        self.faq = faq
        self.comments = comments
        self.rate_score = rate_score
        self.rate_number = rate_number
        self.price = price
        self.versions = versions
        self.public = public
        self.archived = archived
        self.removed = removed

    # For taking from database(!)
    def from_dict(dict: dict):
        return Application(
            dict["name"],
            dict["publisherid"],
            dict["developerid"],
            dict["contact_mail"],
            dict["website"],
            dict["description"],
            dict["icon"],
            dict["screenshots"],
            dict["faq"],
            dict["comments"],
            dict["rate_score"],
            dict["rate_number"],
            dict["price"],
            dict["versions"],
            dict["public"],
            dict["archived"],
            dict["removed"],
            dict["id"],
        )

    # An example version tree before processing (0x068747470733a2f2f7777772e64636f64652e66722f7368613531322d68617368)
    # {
    #   'path/to/file.ext': '0b23b09e77a68e44525113de6ba8ce149852e975bbab8adfe5a8282c243ba90ca4396b7fddc33e88c1ba1e9face31480d0a0940db1ef4252f82fada8dd7d2c64'
    # }
    # or
    # {
    #   [file path]: [hashed content with sha256]
    # }
    #

    def get_version_tree(self, version: str):
        if self.versions.__contains__(version):
            return [
                (("mkdir" if self.versions.get[version][path] == "dir" else "mk"), path)
                for path in self.versions.get[version].keys()
            ]  # mk: Make
        return None

    # Output is (After processing):
    # [
    #   ('mk', 'path/to/file.ext'),
    #   ('mk', 'path/to/another/file.ext')
    # ]

    # If you don't know
    # rmdir: Remove Directory
    # rm: Remove File
    # dir: directories have 'dir' instead of hash code
    # pass: Do Nothing (Just for stability)
    # wo: Write Over File
    # mkdir: Make Directory
    # mk: Make File
    def get_version_delta_tree(self, from_version: str, to_version: str):
        if self.versions.__contains__(from_version) and self.versions.__contains__(
            to_version
        ):
            to = self.versions[to_version]
            fr = self.versions[from_version]

            def get_operation(path, vfrom, vto):
                if path in vfrom and path not in vto:
                    return "rmdir" if vfrom[path] == "dir" else "rm"
                elif path in vfrom and path in vto:
                    if vfrom[path] == vto[path]:
                        return "pass"
                    return "wo"
                elif path not in vfrom and path in vto:
                    return "mkdir" if vto[path] == "dir" else "mk"

            return [
                (get_operation(path, fr, to), path)
                for path in (to.keys() + fr.keys())
                if path not in fr or fr[path] != to[path]
            ]
        return None
