# from dataclasses import dataclass

from pydantic import BaseModel


# @dataclass
class EngineConfig(BaseModel):
    ...


# @dataclass
class LocalRunnerConfig(EngineConfig):
    ...


# @dataclass
class PrefectEngineConfig(EngineConfig):
    use_cached_results: int = False
