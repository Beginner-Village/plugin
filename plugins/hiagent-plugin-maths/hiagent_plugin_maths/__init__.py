import os
import numexpr as ne # type: ignore
from pathlib import Path
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

@set_meta(cn_name="数学工具", en_name="Maths")
class MathsPlugin(BasePlugin):
    """一个用于数学计算的工具。"""
    hiagent_tools = ["eval_expression"]
    hiagent_category = BuiltinCategory.Education

    def eval_expression(self, expr: str) -> str:
        """一个用于计算数学表达式的工具，表达式将通过NumExpr本地执行。"""
        try:
            ret = str(ne.evaluate(expr))
        except Exception as e:
            return f"Invalid expression: {expr}, error: {str(e)}"
        return ret

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"
