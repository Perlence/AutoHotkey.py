class UnsetType:
    def __bool__(self):
        return False

    def __repr__(self):
        return "UNSET"


UNSET = UnsetType()
