"""Basic checking library to create tests for exercises"""
from dataclasses import dataclass
from typing import List


@dataclass
class Check:
    message: str


@dataclass
class TestSuite:
    checks: List[Check]
