from fastapi.testclient import TestClient
from app.api import app
from app.config import BASE_DIR


def test_GetPackageMetadata():
    client = TestClient(app)
    resp = client.post("/v1/GetPackageMetadata", json={
        "pkg": "hiagent-plugin-time",
        "version": "0.1.0",
    })
    data = resp.json()
    assert resp.status_code == 200
    print(data)
    assert data == {
        'data': [{
            'name': 'time',
            'class_name': 'TimePlugin',
            'labels': {'cn_name': '时间工具', 'en_name': 'Time'},
            'description': '一个用于获取当前时间的工具。',
            'icon_uri': f'file://{BASE_DIR}/extensions/hiagent-plugin-time/0.1.0/icon.png',
            'tools': {
                    'current_time': {
                        'name': 'current_time',
                        'labels': {},
                        'description': '获取当前时间',
                        'input_schema': {
                            'properties': {'timezone': {'title': 'Timezone', 'type': 'string'}},
                            'required': ['timezone'],
                            'title': 'InModel',
                            'type': 'object'
                        },
                        'output_schema': {'title': 'OutModel', 'type': 'string'}
                    }
            },
            'config_required': False, 'config_schema': {}
        }],
        'error': None,
    }
