import json
import os
import time

from py_kvstore import KVStore, Pair

current_dir = os.path.dirname(os.path.realpath(__file__))


def verify_dump(kv: KVStore, expected: dict):
    kv.dump()
    with open(kv.get_dump_file(), "r") as f:
        a = json.load(f)
    assert a == expected


def verify_load(kv: KVStore, expected: dict):
    kv.load()
    assert kv.store == expected


def test_expire(
    kv: KVStore,
    sleep_time: float = 1.1,
    expected_expire: list = [],
    still_available: list = [],
):
    time.sleep(sleep_time)

    for exp_expire in expected_expire:
        assert kv.get(exp_expire) is None

    for avail in still_available:
        assert kv.get(avail) is not None


def test_del_key(kv: KVStore, key: str):
    current_keys_len = len(kv.get_keys())
    assert kv.delete(key) is True
    # already deleted
    assert kv.delete(key) is False

    assert len(kv.get_keys()) == current_keys_len - 1


def test_dump_load_after_modification(kv: KVStore):
    # dump to file, load it back and verify again
    current = kv.store
    kv.dump()
    kv.load()
    after = kv.store
    assert current == after


def test_regex(kv: KVStore):
    keys = ["regex;val1;item", "regex;val2;item", "regex;val3;nothing"]
    for k in keys:
        kv.set(k, 1)

    # match all regex;*;item
    res = kv.get_keys("regex;*;item")
    assert len(res) == 2
    kv.delete(keys)


def test_hashset(kv: KVStore):
    kv.hset("hset", "field", "1")
    kv.hset("hset", "field2", "2")

    try:
        # Getting a hset is now allowed
        kv.get("hset")
        assert False
    except Exception as e:
        assert True

    try:
        # getting a normal pair from hset is now allowed
        kv.hget("a", "field")
        assert False
    except Exception as e:
        assert True

    kv.delete("hset")


def test():
    print("Running KV test")
    kv_a = KVStore(name="a", dump_dir=current_dir)

    current_time = int(time.time())

    # Set Initial
    kv_a.set("a", 1, 1)
    kv_a.set("b", 2, 2)
    kv_a.set("c", 3, 3)
    kv_a.set("no_expire", ["test", 1, 2, 3, 4, {"k": "v"}])

    verify_dump(
        kv_a,
        {
            "a": {"value": 1, "timeout": current_time + 1, "ttl_seconds": 1},
            "b": {"value": 2, "timeout": current_time + 2, "ttl_seconds": 2},
            "c": {"value": 3, "timeout": current_time + 3, "ttl_seconds": 3},
            "no_expire": {
                "value": ["test", 1, 2, 3, 4, {"k": "v"}],
                "timeout": -1,
                "ttl_seconds": -1,
            },
        },
    )

    verify_load(
        kv_a,
        {
            "a": Pair(1, current_time + 1),
            "b": Pair(2, current_time + 2),
            "c": Pair(3, current_time + 3),
            "no_expire": Pair(["test", 1, 2, 3, 4, {"k": "v"}], -1),
        },
    )

    # Wait for some expirations
    # time.sleep(2)

    # get a key which has expired
    # assert kv_a.get("a") is None

    # Getting value after expire fails
    test_expire(
        kv_a,
        sleep_time=1,
        expected_expire=["a"],
        still_available=["b", "c", "no_expire"],
    )

    test_del_key(kv_a, "b")

    # this test is likely redundant?
    test_dump_load_after_modification(kv_a)

    test_hashset(kv_a)

    test_regex(kv_a)

    # Cleanup
    os.remove(kv_a.get_dump_file())
    print("KV test passed")


if __name__ == "__main__":
    test()
