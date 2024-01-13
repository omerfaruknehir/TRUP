class Publisher:
    def __init__(
        self,
        name: str,
        userid: int,
        contact_mail: str = "",
        website: str = "",
        description: str = "",
        icon: bytes = None,
        faq: list = [],
        comments: list[int] = [],
        removed: bool = False,
        id=None,
    ):
        self.id = id
        self.name = name
        self.userid = userid
        self.contact_mail = contact_mail
        self.website = website
        self.description = description
        self.icon = icon
        self.faq = faq
        self.comments = comments
        self.removed = removed

    def from_dict(dict: dict):
        return Publisher(
            dict["name"],
            dict["userid"],
            dict["contact_mail"],
            dict["website"],
            dict["description"],
            dict["icon"],
            dict["faq"],
            dict["comments"],
            dict["removed"],
            dict["id"],
        )
