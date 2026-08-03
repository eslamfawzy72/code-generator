

from enum import Enum


class Intent(str, Enum):
    EXPLAIN = "EXPLAIN"
    GENERATE = "GENERATE"