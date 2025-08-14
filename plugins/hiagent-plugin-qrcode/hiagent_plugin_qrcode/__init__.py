from typing import Annotated, Literal
import os
import io
from pathlib import Path

from pydantic import Field
from qrcode.image.base import BaseImage # type: ignore
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q # type: ignore
from qrcode.image.pure import PyPNGImage # type: ignore
from qrcode.main import QRCode # type: ignore

from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory
from hiagent_plugin_sdk.extensions import load

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="二维码工具")
class QRCodePlugin(BasePlugin):
    """一个二维码工具, 用于生成二维码"""
    hiagent_tools = ["qrcode_generator"]
    hiagent_category = BuiltinCategory.LifeAssistant

    error_correction_levels: dict[str, int] = {
        "L": ERROR_CORRECT_L,  # <=7%
        "M": ERROR_CORRECT_M,  # <=15%
        "Q": ERROR_CORRECT_Q,  # <=25%
        "H": ERROR_CORRECT_H,  # <=30%
    }

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def qrcode_generator(self,
        content: Annotated[str, Field(description="二维码文本内容")],
        error_correction: Annotated[Literal["L", "M", "Q", "H"], Field(description='容错等级，可设置为L, M, Q, H，从低到高，生成的二维码越大且容错效果越好')] = "L",
        border: Annotated[int, Field(description="边框粗细的格数（默认为2）0 ~ 100")] = 2,
    ) -> str:
        """生成二维码"""
        if error_correction == "":
            error_correction = "L"
        if border < 0:
            border = 2
        image = self._generate_qrcode(content, border, error_correction)
        buf = io.BytesIO()
        image.save(buf)
        data = buf.getvalue()
        f = io.BytesIO(data)
        # print(f"data: {len(data)}")
        storage = load().storage.get_client()
        return storage.save("qrcode.png", f, length=len(data))

    def _generate_qrcode(self, content: str, border: int, error_correction: str) -> BaseImage:
        qr = QRCode(
            image_factory=PyPNGImage,
            error_correction=self.error_correction_levels.get(error_correction),
            border=border,
        )
        qr.add_data(data=content)
        qr.make(fit=True)
        img = qr.make_image()
        return img

    # @staticmethod
    # def _image_to_byte_array(image: BaseImage) -> bytes:
    #     byte_stream = io.BytesIO()
    #     image.save(byte_stream)
    #     return byte_stream.getvalue()
