
import os
import pytest
import requests
from dotenv import load_dotenv
loaded = load_dotenv("../.env")
from hiagent_plugin_sdk.extensions import load
cfg = load()
print(cfg.model_dump_json(indent=2))


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_redis():
    redis_cli = cfg.redis.get_redis_client()
    ret = redis_cli.ping()
    assert ret == True

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_storage_minio():
    from io import BytesIO
    raw_data = b"hello world"
    storage_cli = cfg.storage.get_client()
    data = BytesIO(raw_data)
    uri = storage_cli.save("test.txt", data, length=11)
    filedata = requests.get(uri).text
    assert filedata == raw_data.decode("utf-8")

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_storage_local():
    from io import BytesIO
    raw_data = b"hello world"
    storage_cli = cfg.storage.local_path.get_client()
    data = BytesIO(raw_data)
    uri = storage_cli.save("test.txt", data)
    with open(uri.removeprefix("file://"), "rb") as f:
        filedata = f.read()
    assert filedata == raw_data
