from openai import OpenAI
import os
import logging
from functools import cache
from hiagent_plugin_sdk.extensions import load
from hiagent_plugin_sdk.utils import rpm_limit

logger = logging.getLogger(__name__)

@cache
def get_client():
    cfg = load().openai
    return OpenAI(
        base_url=cfg.base_url,
        api_key=cfg.api_key,
    )

@rpm_limit(load().openai.rpm)
def chat(user_input: str, system_prompt: str = ""):
    cfg = load().openai
    model_name = cfg.model_name
    client = get_client()
    msgs = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    msgs.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
        model=model_name,
        messages=msgs,
    )
    return completion.choices[0].message.content


def translate(text: str, lang: str, limit: int) -> str:
    # return chat(text, f"You are a translator, please translate the following text to {lang}. within {limit} characters. please return only the translated text, and only one result, no new line.")
    ret = chat(text, f"你是一个多语言翻译器, 请将以下文本翻译成 {lang}. 请在 {limit} 个字符内返回翻译结果, 请直接返回翻译的结果, 去掉收尾的空格, 不需要解释内容. 如果翻译的语音和原文一致, 请返回原文.")
    return ret.strip()

def try_translate(text: str, lang: str, limit: int) -> str:
    try:
        return translate(text, lang, limit)
    except Exception as e:
        logger.error(f"translate {text} to {lang} failed: {e}")
        return ""

if __name__ == "__main__":
    print(chat("hello"))
