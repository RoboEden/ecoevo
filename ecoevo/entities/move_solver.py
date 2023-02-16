from ecoevo.entities import Player
from ecoevo.types import IdType, PosType
from typing import List, Dict, Set
from ortools.linear_solver import pywraplp
from collections import defaultdict
from datetime import datetime
from loguru import logger

class MoveSolver:
    @staticmethod
    def solve(players: List[Player], player_dest: Dict[IdType, PosType]) -> Set[IdType]:
        dts = datetime.now()

        solver = pywraplp.Solver(name='location', problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        
        x = {pid: solver.BoolVar('x_{}'.format(pid)) for pid in player_dest.keys()}
        
        buckets = defaultdict(list)
        for player in players:
            # source point of all player
            buckets[player.pos].append(1 - x.get(player.id, 0))
        for pid, dst in player_dest.items():
            # dest point of moving player
            buckets[dst].append(x[pid])
        
        for bucket in buckets.values():
            solver.Add(sum(bucket) <= 1)

        # objective: maximise the total trading volume
        solver.Maximize(sum(x.values()))

        # solve
        status = solver.Solve()

        # case 1: optimal
        result = set()
        if status == pywraplp.Solver.OPTIMAL:
            logger.debug(f"objective value: {solver.Objective().Value()}")
            for pid, xi in x.items():
                if xi.solution_value() > 0:
                    result.add(pid)
        # case 2: infeasible
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Ineasible!")
        # case 3: others
        else:
            raise Exception("Unexpected status: {}!".format(status))

        dte = datetime.now()
        tm = round((dte - dts).seconds + (dte - dts).microseconds / (10**6), 3)
        logger.debug(f"move model solving time: {tm}s")

        return result