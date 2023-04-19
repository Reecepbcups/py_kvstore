# Redis has a feature where you can set a timeout for a key.
# Do this with a local dictionary. have a .set method which sets a key, value, and timeout.
# if no timeout is specified, set it as -1.

import json
import os
import re as regex
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

current_dir = os.path.dirname(os.path.realpath(__file__))


class StoreType(Enum):
    PAIR = "pair"
    HASHSET = "hashset"

    def __str__(self):
        return self.value


@dataclass
class Pair:
    value: Any
    timeout: int
    store_type: str = str(StoreType.PAIR)

    def toJSON(self):
        return {
            "value": self.value,
            "timeout": self.timeout,
            "ttl_seconds": self.get_ttl_seconds(),
        }

    def get_ttl_seconds(self):
        return -1 if self.timeout == -1 else self.timeout - int(time.time())

    @staticmethod
    def fromJSON(json: dict):
        return Pair(json["value"], json["timeout"])


@dataclass
class HashSet(Pair):
    value: dict[str, Any]
    timeout: int
    store_type: str = str(StoreType.HASHSET)


class KVStore:
    # TODO: Specify in memory or on the disk (slower, but better for large data sets)
    def __init__(self, name: Optional[str] = None, dump_dir: str = ""):
        self.name = name
        self.store: dict[str, Pair] = {}

        self.dump_dir = current_dir
        if len(dump_dir) > 0:
            self.dump_dir = dump_dir

    def get_dump_dir(self):
        return self.dump_dir

    def get_dump_file(self):
        return os.path.join(self.dump_dir, f"{self.name}.json")

    def __check_type(self, key: str, store_type: StoreType):
        if self.store[key].store_type != str(store_type):
            raise Exception(f"Key {key} is not a {store_type}")

    def __value_not_expired(self, value: Pair | HashSet):
        return value.timeout == -1 or value.timeout > int(time.time())

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

    # hash set and hash get
    # You can only set the expire time on creation?
    def hset(self, key: str, field: str, value: Any, timeout: int = -1):
        self.delete_expired_data_if_applicable(key)

        if key not in self.store:
            # timeout can only be set on creation
            current_time = int(time.time())
            self.store[key] = HashSet({}, current_time + timeout)
        else:
            if self.store[key].store_type != "hashset":
                raise Exception(f"Key {key} is not a hashset")

        # grab the current hset
        hset = self.store[key].value
        hset[field] = value
        # reset the store value
        self.store[key].value = hset

    def hset_expire(self, key: str, timeout: int = -1):
        if key not in self.store:
            raise Exception(f"Key {key} does not exist")

        self.store[key].timeout = timeout

    def hget(self, key: str, field: str) -> Any | None:
        self.delete_expired_data_if_applicable(key)
        if key not in self.store:
            return None

        if field not in self.store[key].value:
            return None

        self.__check_type(key, StoreType.HASHSET)

        return self.store[key].value[field]

    def incr(self, key: str, amount: int = 1) -> int:
        """Returns the new value"""
        if key not in self.store:
            self.set(key, amount)
            return amount

        self.__check_type(key, StoreType.PAIR)

        if not isinstance(self.store[key].value, int):
            raise Exception(f"key:{key}'s value is not an int")

        self.store[key].value += amount
        return self.store[key].value

    def get(self, key) -> Any | None:
        self.delete_expired_data_if_applicable(key)

        if key in self.store:
            self.__check_type(key, StoreType.PAIR)

            return self.store[key].value
        return None

    def get_keys(self, search_regex: str = "") -> list[str]:
        search_regex = search_regex.replace("*", ".+")
        self.delete_all_expired_data()
        if len(search_regex) == 0:
            return list(self.store.keys())
        else:
            return [k for k in self.store.keys() if regex.match(search_regex, k)]

    def delete(self, keys: str | list[str]) -> bool:
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            if key in self.store:
                del self.store[key]
            else:
                return False
        return True

    def clear(self):
        self.store.clear()

    def ttl_seconds(self, key) -> int | None:
        self.delete_expired_data_if_applicable(key)
        if key in self.store:
            p = self.store[key]
            return p.get_ttl_seconds()
        return None

    def dbg(self):
        self.delete_all_expired_data()
        print("dbg", self.name, self.dump_dir, self.store)

    def delete_all_expired_data(self):
        self.store = {
            k: v for k, v in self.store.items() if self.__value_not_expired(v)
        }

    def delete_expired_data_if_applicable(self, keys: str | list[str]) -> int:
        """
        Returns an int of the number of keys removed
        """
        if isinstance(keys, str):
            keys = [keys]

        found = 0
        for k in keys:
            if k in self.store:
                timeout = self.store[k].timeout
                if timeout >= 0 and timeout <= int(time.time()):
                    del self.store[k]
                    found += 1
        return found

    def dump(self):
        file = self.get_dump_file()
        with open(file, "w") as f:
            json.dump(
                self.store,
                f,
                default=lambda o: o.toJSON(),
            )
        self.delete_all_expired_data()

    def load(self):
        file = self.get_dump_file()
        if not os.path.isfile(file):
            return

        with open(file, "r") as f:
            pre_store = json.load(f)

        for key, value in pre_store.items():
            p = Pair.fromJSON(value)
            if self.__value_not_expired(p):
                self.store[key] = p

    # def __del__(self):
    #     # on close of program, dump the data to a file
    #     # print("Garbage Collection: Dumping to file for storage")
    #     self.dump()

    def __str__(self):
        self.delete_all_expired_data()
        return f"Name: {self.name}, Store Keys Amount: {len(self.store)}"

    def to_json(self) -> dict:
        self.delete_all_expired_data()
        return json.loads(json.dumps(self.store, default=lambda o: o.toJSON()))


def main():
    kv1 = KVStore(name="transactions")

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

        kv1.set("counter", 0)
        v = kv1.incr("counter")
        print(kv1.get("counter"), v)  # 1
        v = kv1.incr("counter", 5)
        print(kv1.get("counter"), v)  # 6

        # set counter as a string fails
        # kv1.set("counter", "0")
        # kv1.incr("counter")


if __name__ == "__main__":
    main()
