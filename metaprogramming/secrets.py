import inspect
from abc import ABCMeta, abstractmethod
from textwrap import dedent
from typing import List


class Secret(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user(self) -> str:
        """Provide username for secret"""

    @property
    @abstractmethod
    def pwd(self) -> str:
        """Provide encoded password for secret"""

    @abstractmethod
    def show_pwd(self) -> str:
        """Provide raw password for secret"""

    def __repr__(self) -> str:
        class_name = type(self).__name__
        properties = {
            attr: getattr(self, attr)
            for attr in dir(type(self))
            if isinstance(getattr(type(self), attr), property)
        }
        properties_str = ", ".join(
            [f'{prop}={val}' for prop, val in properties.items()]
        )
        return f"{class_name}({properties_str})"


class GenericSecret(Secret):

    def __init__(self, usr, pwd):
        self._usr = usr
        self._pwd = pwd

    @property
    def user(self) -> str:
        return self._usr

    @property
    def pwd(self) -> str:
        return "*" * len(self._pwd)

    def show_pwd(self) -> str:
        return self._pwd


class DbSecret(GenericSecret):

    def __init__(self, usr, pwd, connection_string):
        super().__init__(usr, pwd)
        self._conn = connection_string

    @property
    def conn_str(self) -> str:
        return self._conn


class SecretStore:

    @staticmethod
    def secret_types() -> List[Secret]:
        return [GenericSecret, DbSecret]

    def __init__(self):
        self._secrets: List[Secret] = []
        self._generate_secret_adders()

    def _generate_secret_adders(self) -> None:
        """Metaprogramming to create `add_<secret>` functions for `secret_types`."""
        for secret_type in SecretStore.secret_types():
            method_name = f"add_{secret_type.__name__.lower()}"
            method_signature = inspect.signature(secret_type)
            parameters = ", ".join(method_signature.parameters.keys())
            method_str = dedent(f"""
            def {method_name}(self, {parameters}):
                self._secrets.append({secret_type.__name__}({parameters}))
            """)
            local_scope = {}
            exec(method_str, globals(), local_scope)
            setattr(self, method_name, local_scope[method_name].__get__(self))

    @property
    def secrets(self) -> List[Secret]:
        return self._secrets


if __name__ == "__main__":
    print("Creating a GenericSecret...")
    generic_secret = GenericSecret("tom", "pwd123!")
    print(generic_secret)

    print("\nCreating a DbSecret...")
    dev_db_secret = DbSecret("tom", "dbPwd123!", "localhost:5000")
    print(dev_db_secret)

    print("\n\nUsing a SecretStore to create secrets:")
    store = SecretStore()
    print("First let's see the `add_*` methods created using metaprogramming:")
    print([attr for attr in dir(store) if attr.startswith("add")])
    print(f"No secrets starting out: {store.secrets}")
    store.add_genericsecret("zach", "caspwd123!")
    store.add_dbsecret("zach", "213ffa", "localhost:9092")
    print(f"Secrets created using `add_*` methods: {store.secrets}")