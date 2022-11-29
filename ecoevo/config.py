from dataclasses import dataclass


@dataclass
class EnvConfig:
    agent_num: int
    total_step: int
    