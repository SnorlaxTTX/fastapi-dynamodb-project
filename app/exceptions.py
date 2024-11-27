class StandardException(Exception):
    def __init__(self, type: str, title: str, status: int, detail: str):
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
