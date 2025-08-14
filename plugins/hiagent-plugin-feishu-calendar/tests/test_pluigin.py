import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_calendar import FeishuCalendarPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuCalendarPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_calendars():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    req = {
        "page_size": 500,
    }
    ret = await ins.list_calendars(**req)
    print(ret)
    assert len(ret.data.calendar_list) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_event():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "idempotency_key": "25fdf41b-8c80-2ce1-e94c-de8b5e7aa7e6",
        "event": {
            "summary": "日程标题",
            "description": "日程描述",
            "need_notification": False,
            "start_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            },
            "end_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            },
        }
    }
    ret = await ins.create_event(**req)
    print(ret)
    assert ret.data.event is not None
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_delete_event():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "event_id": "bbf06c88-442c-c4ef-3b6b-803acba63d8d_0",
    }
    ret = await ins.delete_event(**req)
    print(ret)
    assert ret.code == 0
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_event():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    import time
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "anchor_time": "1509430400" # time.time_ns() // 1000^3,
    }
    ret = await ins.list_event(**req)
    print(ret)
    assert ret.code == 0
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_update_event():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "event_id": "48949064-447f-42aa-92bf-a86017a89cb3_0",
        "event": {
            "summary": "日程标题2",
            "description": "日程描述2",
            "need_notification": False,
            "start_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            },
            "end_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            },
        }
    }
    ret = await ins.update_event(**req)
    print(ret)
    assert ret.code == 0
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_search_event():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    import time
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "query": "日程标题",
        "filter": {
            "start_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            },
            "end_time": {
                "date": "2018-09-01",
                "timestamp": "1602504000",
                "timezone": "Asia/Shanghai"
            }
        }
    }
    ret = await ins.search_event(**req)
    print(ret)
    assert len(ret.data.items) > 0
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_event_attendee():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuCalendarPlugin(**cfg_dict)
    import time
    req = {
        "calendar_id": "feishu.cn_hKUYVtj4OKdyLFpm2GWTkf@group.calendar.feishu.cn",
        "event_id": "48949064-447f-42aa-92bf-a86017a89cb3_0",
        "attendees": [{
            "third_party_email": "archever@163.com",
            "type": "third_party",
        }]
    }
    ret = await ins.create_event_attendee(**req)
    print(ret)
    assert len(ret.data.attendees) > 0
    assert False
