from fastapi.testclient import TestClient
from app.api import app


def test_run_tool():
    client = TestClient(app)
    resp = client.post("/v1/RunPluginTool", json={
        "pkg": "hiagent-plugin-time",
        "version": "0.1.0",
        "plugin": "time",
        "tool": "current_time",
        "input": {
            "timezone": "Asia/Shanghai"
        },
    })

    data = resp.json()
    assert resp.status_code == 200
    print(data)
    assert data.get("data") != ""
