class ObjectAlreadyExists(Exception):
    def __init__(self, *args: object) -> None:
       super().__init__(*args)

class CannotFindObject(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)