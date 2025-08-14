from pathlib import Path
import os

def get_base_dir() -> Path:
    c = os.path.dirname(os.path.abspath(__file__))
    return Path(c).parent.parent


BASE_DIR = get_base_dir()
EXT_SECRET = "x-hiagent-secret"
EXT_DESC_EN = "x-description-en"
EXT_DESC_ZH_HANS = "x-description-zh-hans"
EXT_DESC_ZH_HANT = "x-description-zh-hant"

META_PREFIX = "_hiagent_"

if __name__ == "__main__":
    print(BASE_DIR)
