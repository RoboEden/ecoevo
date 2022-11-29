from dataclasses import dataclass


@dataclass
class EnvConfig:
    NUM_AGENTS: int
    TRAJ_LEN: int
    