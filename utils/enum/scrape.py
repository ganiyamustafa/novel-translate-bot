from enum import Enum

class TranslateOutputType(Enum):
  STRING = 0
  LIST_STRING = 1

class NovelSource(Enum):
  SYOSETSU = 0
  KAKUYOMU = 1