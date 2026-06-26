from DiploGM.repositories.extension import ExtensionEventRepository


class RepositoryFactory:
    REGISTRY = {"extension": ExtensionEventRepository}

    @classmethod
    def create(cls, type=""):
        _cls = cls.REGISTRY.get(type, None)
        if _cls is None:
            raise

        return _cls()
