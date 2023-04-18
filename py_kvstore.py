# Redis has a feature where you can set a timeout for a key.
# Do this with a local dictionary. have a .set method which sets a key, value, and timeout.
# if no timeout is specified, set it as -1.

import json
import os
import re as regex
import time
from dataclasses import dataclass
from typing import Any, Optional

current_dir = os.path.dirname(os.path.realpath(__file__))


@dataclass
class Pair:
    value: Any
    timeout: int

    def toJSON(self):
        return {"value": self.value, "timeout": self.timeout}

    @staticmethod
    def fromJSON(json: dict):
        return Pair(json["value"], json["timeout"])


class KV:
    def __init__(self, name: Optional[str] = None, dump_dir=None):
        self.name = name
        self.store: dict[str, Pair] = {}

        self.dump_dir = current_dir
        if dump_dir is not None:
            self.dump_dir = dump_dir

    def set(self, key: str, value: Any, timeout: int = -1):
        """
        -1: no timeout
        0: delete key time
        > 0: timeout in seconds (epoch)
        """
        if len(key) == 0:
            raise Exception("Key cannot be empty")

        # Overrides previous set value and deletes if set as 0
        if timeout == 0:
            del self.store[key]
            return

        if timeout > 0:
            timeout += int(time.time())

        self.store[key] = Pair(value, timeout)

    def get(self, key) -> Any | None:
        self.delete_expired_data_if_applicable(key)

        if key in self.store:
            return self.store[key].value
        return None

    def get_keys(self, search_regex: str = "") -> list[str]:
        self.delete_all_expired_data()
        if len(search_regex) == 0:
            return list(self.store.keys())
        else:
            return [k for k in self.store.keys() if regex.match(search_regex, k)]

    def delete(self, key) -> bool:
        if key in self.store:
            del self.store[key]
            return True
        return False

    def ttl(self, key) -> int:
        self.delete_expired_data_if_applicable(key)
        if key in self.store:
            p = self.store[key]
            return p.timeout
        return -2

    def dbg(self):
        self.delete_all_expired_data()
        print("dbg", self.store)

    def delete_all_expired_data(self):
        current_time = int(time.time())
        self.store = {
            k: v
            for k, v in self.store.items()
            if v.timeout >= current_time or v.timeout == -1
        }

    def delete_expired_data_if_applicable(self, key: str):
        if key in self.store:
            timeout = self.store[key].timeout
            if timeout >= 0 and timeout < int(time.time()):
                del self.store[key]

    def dump(self):
        file = os.path.join(self.dump_dir, f"{self.name}.json")

        with open(file, "w") as f:
            json.dump(
                self.store,
                f,
                default=lambda o: o.toJSON(),
            )

        self.delete_all_expired_data()

    def load(self):
        current_time = int(time.time())

        file = os.path.join(self.dump_dir, f"{self.name}.json")
        with open(file, "r") as f:
            pre_store = json.load(f)

        for key, value in pre_store.items():
            p = Pair.fromJSON(value)
            if p.timeout <= current_time and p.timeout != -1:
                continue
            self.store[key] = p


def main():
    kv1 = KV(name="transactions")

    if True:
        kv1.set("dict", {"test": "other value"})
        kv1.set("list", [])
        kv1.set("apple", 2, 1)
        kv1.set("airplane", 2, 1)
        kv1.set("grass", 2, 1)
        kv1.set("b", 2, 1)
        kv1.set("c", 3, 2)
        kv1.set("c", 3, 30)
        kv1.set("d", [1, 2, 3, 4], 30)
        kv1.set("1d", [1, 2, 3, 4], 30)
        # print(kv1.get("dict"))

        print(kv1.get_keys("a."))  # apple airplane
        print(kv1.get_keys("a.|grass"))  # apple airplane, grass

        # kv1.dbg()
        # kv1.dump()


main()
