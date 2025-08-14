from fastapi.testclient import TestClient
from app.api import app
from app.config import BASE_DIR


def test_install_pkg():
    client = TestClient(app)
    pkg = "hiagent_plugin_time-0.1.0-py3-none-any.whl"
    uri = f"file://{BASE_DIR}/dist/{pkg}"
    resp = client.post("/v1/InstallPackage", json={
        "uri":uri,
        "filename": pkg,
    })
    print(f"file://{BASE_DIR}/dist/{pkg}")
    data = resp.json()
    assert resp.status_code == 200
    print(data)
    assert data == {
        'data': {
            'name': 'hiagent-plugin-time',
            'version': '0.1.0',
            'uri': uri,
            'filename': 'hiagent_plugin_time-0.1.0-py3-none-any.whl',
            'plugins': [{
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
                'config_required': False, 'config_schema': {}}
            ]},
        'error': None
    }
