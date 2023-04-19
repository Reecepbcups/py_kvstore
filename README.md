# py_kvstore

A simple Key-Value store (similar to redis) built in python.

Sets can expire, not expire, and be saved with any arbitrary data. So you can set it as a JSON string, a dict, int, or any other value. It is up to the developer to implement and parse types correctly.

## Notable Features

```py
# create a new KVStore
kv1 = KVStore(name="transactions", dump_dir="/home/reece/kvstores")

# Set a key. Defaults to -1 timeout (no timeout)
kv1.set("tx;UUID-HERE", "{"data":{"time":"...","amount":"...","currency":"..."}}")

# Get the key, returns None if not found (ex: expired or never set)
res = kv1.get("tx;UUID-HERE")

# Set this key to expire in 100 seconds
kv1.set("other;expire_later", "some string here", 100)

# Store data in multiple sub keys (hashset).
# You can only set a timeout on the parent key for now IF its a new set. Else use .hset_expire(...)
kv1.hset("parent_key", "subkey1", "value", 10)
kv1.hset("parent_key", "subkey2", "value2")

kv1.hget("parent_key", "subkey1") # returns "value"

# Set values and increment a counter
kv1.set("counter", 0)
kv1.incr("counter") # returns 1
kv1.incr("counter", amount=4) # returns 5

# Keys
kv1.get_keys() # returns all non expired keys
kv1.get_keys("tx;*") # returns keys matching the regex

# Save current memory state to disk (the dump_dir set on initialize.)
kv1.dump()

# clear the store
kv1.clear()

# Load the previous dump from file
kv1.load()
```

## Example Repos using this

- [Cosmos Endpoint Cache](https://github.com/Reecepbcups/cosmos-endpoint-cache)