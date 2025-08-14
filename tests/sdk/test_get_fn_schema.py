from typing import Annotated
from pydantic import Field, BaseModel
from hiagent_plugin_sdk.utils import get_fn_schema


def test_annotated_def():
    def test(a: int, b: int, c: str, d: float, e: bool, f: list[int] = [], g: dict[str, int] = {}) -> str:
        """test"""
        return "test"
    input_schema, output_schema = get_fn_schema(test)
    assert input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
            "b": {
                "title": "B",
                "type": "integer"
            },
            "c": {
                "title": "C",
                "type": "string"
            },
            "d": {
                "title": "D",
                "type": "number"
            },
            "e": {
                "title": "E",
                "type": "boolean"
            },
            "f": {
                'default': [],
                "title": "F",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            },
            "g": {
                'default': {},
                "title": "G",
                "type": "object",
                "additionalProperties": {
                    "type": "integer"
                }
            }
        },
        "required": [
            "a",
            "b",
            "c",
            "d",
            "e",
        ]
    }
    assert output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "string"
    }


def test_annotated_method():
    class Test:
        def __init__(self, a: int, b: int = 1):
            """test"""

        def method(self, a: int = 1, b: int = 1) -> None:
            """test"""

        @classmethod
        def method2(cls, a: int, b: int) -> str:
            """test"""
            return "test"

        @staticmethod
        def method3(a: int, b: int = 1) -> int:
            """test"""
            return 1
    config_schema, _ = get_fn_schema(Test.__init__, Test, ignore_return_not_set=True)
    assert config_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
            "b": {
                "title": "B",
                "type": "integer",
                "default": 1,
            },
        },
        "required": [
            "a",
        ]
    }
    method_input_schema, method_output_schema = get_fn_schema(
        Test.method, Test)
    assert method_input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer",
                "default": 1,
            },
            "b": {
                "title": "B",
                "type": "integer",
                "default": 1,
            },
        },
    }
    assert method_output_schema.model_json_schema() == {
        "title": "NullModel",
        "type": "null"
    }
    method2_input_schema, method2_output_schema = get_fn_schema(
        Test.method2, Test)
    assert method2_input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
            "b": {
                "title": "B",
                "type": "integer"
            },
        },
        "required": [
            "a",
            "b",
        ]
    }
    assert method2_output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "string"
    }
    method3_input_schema, method3_output_schema = get_fn_schema(
        Test.method3, Test)
    assert method3_input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
            "b": {
                "title": "B",
                "type": "integer",
                "default": 1,
            },
        },
        "required": [
            "a",
        ]
    }
    assert method3_output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "integer"
    }


def test_annotated_field():
    def add(
            a: Annotated[int, Field(description="param a")],
            b: Annotated[int, Field(description="param b")] = 1) -> int:
        """test"""
        return a + b
    input_schema, output_schema = get_fn_schema(add)
    assert input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer",
                "description": "param a",
            },
            "b": {
                "title": "B",
                "type": "integer",
                "description": "param b",
                "default": 1,
            },
        },
        "required": [
            "a",
        ]
    }
    assert output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "integer"
    }


def test_annotated_model():
    class Req(BaseModel):
        a: int
        b: int = 1
        c: int = Field(description="param c", default=2)

    def add(req: Req) -> int:
        """test"""
        return req.a + req.b + req.c
    input_schema, output_schema = get_fn_schema(add)
    assert input_schema.model_json_schema() == {
        '$defs': {
            'Req': {
                'properties': {
                    'a': {
                        'title': 'A',
                        'type': 'integer',
                    },
                    'b': {
                        'default': 1,
                        'title': 'B',
                        'type': 'integer',
                    },
                    'c': {
                        'default': 2,
                        'description': 'param c',
                        'title': 'C',
                        'type': 'integer',
                    },
                },
                'required': [
                    'a',
                ],
                'title': 'Req',
                'type': 'object',
            },
        },
        "title": "InModel",
        "type": "object",
        "properties": {
            "req": {
                "$ref": "#/$defs/Req",
            },
        },
        "required": [
            "req",
        ]
    }
    assert output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "integer"
    }


def test_annotated_varkwargs():
    def add(a: int, **kwargs: int) -> int:
        """test"""
        return a + sum(kwargs.values())
    input_schema, output_schema = get_fn_schema(add)
    assert input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        'additionalProperties': True,
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
        },
        "required": [
            "a",
        ]
    }
    assert output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "integer"
    }


def test_annotated_kwargs():
    def add(a: int, *, b: int, c: int = 1) -> int:
        """test"""
        return a + b + c
    input_schema, output_schema = get_fn_schema(add)
    assert input_schema.model_json_schema() == {
        "title": "InModel",
        "type": "object",
        "properties": {
            "a": {
                "title": "A",
                "type": "integer"
            },
            "b": {
                "title": "B",
                "type": "integer"
            },
            "c": {
                "title": "C",
                "type": "integer",
                "default": 1,
            },
        },
        "required": [
            "a",
            "b",
        ]
    }
    assert output_schema.model_json_schema() == {
        "title": "OutModel",
        "type": "integer"
    }