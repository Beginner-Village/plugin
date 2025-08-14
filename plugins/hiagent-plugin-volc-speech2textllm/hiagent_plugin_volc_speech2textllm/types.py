from typing import List
from pydantic import BaseModel

class UtterancesAdditions(BaseModel):
  speaker: str = ""

class Utterances(BaseModel):
  end_time: int = 0
  start_time: int = 0
  text: str = ""
  additions: UtterancesAdditions | None = None

class AudioInfo(BaseModel):
  duration: int = 0

class Result(BaseModel):
  text: str = ""
  utterances: List[Utterances] | None = None

class Resp(BaseModel):
  audio_info: AudioInfo | None = None
  result: Result | None = None
