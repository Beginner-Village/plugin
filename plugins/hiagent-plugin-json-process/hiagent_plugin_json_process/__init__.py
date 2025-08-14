from typing import Annotated, Literal
import os
import json
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory
from jsonpath_ng import parse # type: ignore

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="json处理")
class JsonProcessPlugin(BasePlugin):
    """利用 jsonpath_ng 处理 JSON 内容的工具"""
    hiagent_tools = ["parse", "replace", "delete", "insert"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def parse(self,
        json_filter: Annotated[str, Field(description='需要解析的 JSON 字段')],
        content: Annotated[str, Field(description="JSON文件内容")],
        ensure_ascii: Annotated[bool, Field(description="确保输出的 JSON 是 ASCII 编码")] = False,
    ) -> str:
        """一个解析JSON对象的工具"""
        input_data = json.loads(content)
        expr = parse(json_filter)
        result = [match.value for match in expr.find(input_data)]

        if not result:
            return ""

        if len(result) == 1:
            result = result[0]

        if isinstance(result, dict | list):
            return json.dumps(result, ensure_ascii=ensure_ascii)
        elif isinstance(result, str | int | float | bool) or result is None:
            return str(result)
        else:
            return repr(result)

    async def delete(self,
        query: Annotated[str, Field(description='用于定位元素的 JSONPath 查询')],
        content: Annotated[str, Field(description="JSON文件内容")],
        ensure_ascii: Annotated[bool, Field(description="确保输出的 JSON 是 ASCII 编码")] = False,
    ) -> str:
        """一个删除 JSON 内容的工具"""
        input_data = json.loads(content)
        expr = parse("$." + query.lstrip("$."))  # Ensure query path starts with $

        matches = expr.find(input_data)

        if not matches:
            return json.dumps(input_data, ensure_ascii=ensure_ascii)  # No changes if no matches found

        for match in matches:
            if isinstance(match.context.value, dict):
                # Delete key from dictionary
                del match.context.value[match.path.fields[-1]]
            elif isinstance(match.context.value, list):
                # Remove item from list
                match.context.value.remove(match.value)
            else:
                # For other cases, we might want to set to None or remove the parent key
                parent = match.context.parent
                if parent:
                    del parent.value[match.path.fields[-1]]

        return json.dumps(input_data, ensure_ascii=ensure_ascii)

    async def insert(self,
        query: Annotated[str, Field(description='用于定位元素的 JSONPath 查询')],
        content: Annotated[str, Field(description="JSON文件内容")],
        new_value: Annotated[str, Field(description="插入的新值")],
        value_decode: Annotated[bool, Field(description="是否将值解码为 JSON 对象")] = False,
        create_path: Annotated[bool, Field(description="是否创建路径")] = False,
        ensure_ascii: Annotated[bool, Field(description="确保输出的 JSON 是 ASCII 编码")] = False,
    ) -> str:
        """一个插入 JSON 内容的工具"""
        input_data = json.loads(content)
        expr = parse(query)
        if value_decode is True:
            try:
                new_value = json.loads(new_value)
            except json.JSONDecodeError:
                return "Cannot decode new value to json object"

        matches = expr.find(input_data)

        if not matches and create_path:
            # create new path
            path_parts = query.strip("$").strip(".").split(".")
            current = input_data
            for i, part in enumerate(path_parts):
                if "[" in part and "]" in part:
                    # process array index
                    array_name, index_str = part.split("[")
                    index = int(index_str.rstrip("]"))
                    if array_name not in current:
                        current[array_name] = []
                    while len(current[array_name]) <= index:
                        current[array_name].append({})
                    current = current[array_name][index]
                else:
                    if i == len(path_parts) - 1:
                        current[part] = new_value
                    elif part not in current:
                        current[part] = {}
                    current = current[part]
        else:
            for match in matches:
                if isinstance(match.value, dict):
                    # insert new value into dict
                    if isinstance(new_value, dict):
                        match.value.update(new_value)
                    else:
                        raise ValueError("Cannot insert non-dict value into dict")
                elif isinstance(match.value, list):
                    # insert new value into list
                    if index is None:
                        match.value.append(new_value)
                    else:
                        match.value.insert(int(index), new_value)
                else:
                    # replace old value with new value
                    match.full_path.update(input_data, new_value)

        return json.dumps(input_data, ensure_ascii=ensure_ascii)

    async def replace(self,
        query: Annotated[str, Field(description='用于定位元素的 JSONPath 查询')],
        content: Annotated[str, Field(description="JSON文件内容")],
        replace_value: Annotated[str, Field(description="替换值")],
        replace_pattern: Annotated[str, Field(description="待替换字符串")] = "",
        replace_model: Annotated[Literal["key", "value", "pattern"], Field(description="替换模式: key: 键替换, value: 值替换, pattern: 字符串替换")] = "value",
        value_decode: Annotated[bool, Field(description="是否将值解码为 JSON 对象")] = False,
        ensure_ascii: Annotated[bool, Field(description="确保输出的 JSON 是 ASCII 编码")] = False,
    ) -> str:
        """一个替换 JSON 内容的工具"""
        if replace_model == "pattern":
            if not replace_pattern:
                return "Invalid parameter replace_pattern"
            result = self._replace_pattern(
                content, query, replace_pattern, replace_value, ensure_ascii, value_decode
            )
        elif replace_model == "key":
            result = self._replace_key(content, query, replace_value, ensure_ascii)
        elif replace_model == "value":
            result = self._replace_value(content, query, replace_value, ensure_ascii, value_decode)
        return str(result)

    # Replace pattern
    def _replace_pattern(
        self, content: str, query: str, replace_pattern: str, replace_value: str, ensure_ascii: bool, value_decode: bool
    ) -> str:
        try:
            input_data = json.loads(content)
            expr = parse(query)

            matches = expr.find(input_data)

            for match in matches:
                new_value = match.value.replace(replace_pattern, replace_value)
                if value_decode is True:
                    try:
                        new_value = json.loads(new_value)
                    except json.JSONDecodeError:
                        return "Cannot decode replace value to json object"

                match.full_path.update(input_data, new_value)

            return json.dumps(input_data, ensure_ascii=ensure_ascii)
        except Exception as e:
            return str(e)

    # Replace key
    def _replace_key(self, content: str, query: str, replace_value: str, ensure_ascii: bool) -> str:
        try:
            input_data = json.loads(content)
            expr = parse(query)

            matches = expr.find(input_data)

            for match in matches:
                parent = match.context.value
                if isinstance(parent, dict):
                    old_key = match.path.fields[0]
                    if old_key in parent:
                        value = parent.pop(old_key)
                        parent[replace_value] = value
                elif isinstance(parent, list):
                    for item in parent:
                        if isinstance(item, dict) and old_key in item:
                            value = item.pop(old_key)
                            item[replace_value] = value
            return json.dumps(input_data, ensure_ascii=ensure_ascii)
        except Exception as e:
            return str(e)

    # Replace value
    def _replace_value(
        self, content: str, query: str, replace_value: str, ensure_ascii: bool, value_decode: bool
    ) -> str:
        try:
            input_data = json.loads(content)
            expr = parse(query)
            if value_decode is True:
                try:
                    replace_value = json.loads(replace_value)
                except json.JSONDecodeError:
                    return "Cannot decode replace value to json object"

            matches = expr.find(input_data)

            for match in matches:
                match.full_path.update(input_data, replace_value)

            return json.dumps(input_data, ensure_ascii=ensure_ascii)
        except Exception as e:
            return str(e)

