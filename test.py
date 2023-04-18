import json
import os
import time

from py_kvstore import KV, Pair, current_dir


def test():
    print("Running KV test")
    kv_a = KV(name="a")
    kv_a_file = os.path.join(current_dir, "a.json")

    current_time = int(time.time())

    kv_a.set("a", 1, 1)
    kv_a.set("b", 2, 2)
    kv_a.set("c", 3, 3)
    kv_a.set("no_expire", ["test", 1, 2, 3, 4, {"k": "v"}])

    # Verify the dump matches
    kv_a.dump()
    with open(kv_a_file, "r") as f:
        a = json.load(f)

    assert a == {
        "a": {"value": 1, "timeout": current_time + 1},
        "b": {"value": 2, "timeout": current_time + 2},
        "c": {"value": 3, "timeout": current_time + 3},
        "no_expire": {"value": ["test", 1, 2, 3, 4, {"k": "v"}], "timeout": -1},
    }

    # ensure the load matches actual Pair objects expected
    kv_a.load()
    assert kv_a.store == {
        "a": Pair(1, current_time + 1),
        "b": Pair(2, current_time + 2),
        "c": Pair(3, current_time + 3),
        "no_expire": Pair(["test", 1, 2, 3, 4, {"k": "v"}], -1),
    }

    time.sleep(2)

    # get a key which has expired
    assert kv_a.get("a") is None

    # Succcessfully deletes a key which is in the store
    res = kv_a.delete("b")
    assert res is True

    res = kv_a.delete("b")
    assert res is False

    # get a key which has not expired
    assert kv_a.get("c") == 3

    time.sleep(1)
    # get all keys, this should remove expired keys
    assert kv_a.get_keys() == ["c", "no_expire"]

    # dump to file, load it back and verify again
    current = kv_a.store
    kv_a.dump()
    kv_a.load()
    after = kv_a.store
    assert current == after

    # remove the file
    os.remove(kv_a_file)

    # TODO: Add regex test

    print("KV test passed")


test()
