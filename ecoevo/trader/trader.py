
from datetime import datetime
from typing import List, Dict, Tuple

from ortools.linear_solver import pywraplp


class Trader(object):
    """
    trader
    """
    def __init__(self, list_order: List[Tuple[Tuple[int, int], Tuple[str, int], Tuple[str, int]]]) -> None:
        """
        trader, initialise

        :param list_order:  list of orders
        """

        self.list_order = list_order

        # data process for model
        self.mat_if_match, self.mat_volume = self._process()

        # model result
        self.list_match = []

    def _process(self) -> Tuple[List[List[bool]], List[List[int]]]:
        """
        data process for model

        :return: mat_if_match:  available matching matrix
        :return: mat_volume:  trading volume matrix
        """

        order_distance = 4  # TODO

        mat_if_match = [[False for _ in self.list_order] for _ in self.list_order]
        mat_volume = [[0 for _ in self.list_order] for _ in self.list_order]
        for i in range(len(self.list_order)):
            for j in range(len(self.list_order)):
                # jump over same orders
                if i == j:
                    continue

                # too far to trade
                pos_i, pos_j = self.list_order[i][0], self.list_order[j][0]
                if abs(pos_i[0] - pos_j[0]) > order_distance or abs(pos_i[1] - pos_j[1]) > order_distance:
                    continue

                # items cannot match
                if self.list_order[j][2][0] != self.list_order[i][1][0] or self.list_order[
                    j][1][0] != self.list_order[i][2][0]:
                    continue

                # item ratio cannot match
                if self.list_order[i][1][1] * self.list_order[j][1][1] != self.list_order[
                    i][2][1] * self.list_order[j][2][1]:
                    continue

                mat_if_match[i][j] = True
                mat_volume[i][j] = min(abs(self.list_order[i][1][1]), self.list_order[i][2][1], abs(
                    self.list_order[j][1][1]), self.list_order[j][2][1])

        return mat_if_match, mat_volume
    
    def trade(self):
        """
        IP Model for automated trade matching

        :return: dict_match:  matching list, (order index, order index)
        """

        # parameters
        num_order = len(self.list_order)
        mat_if_match = self.mat_if_match
        mat_volume = self.mat_volume

        solver = pywraplp.Solver(name='location', problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        
        # variable: if choose a match
        x = [[solver.BoolVar('x_{}_{}'.format(i, j)) for j in range(num_order)] for i in range(num_order)]

        # constraint: validation
        for i in range(num_order):
            for j in range(num_order):
                solver.Add(x[i][j] <= mat_if_match[i][j])

        # constraint: symmetry
        for i in range(num_order):
            for j in range(num_order):
                solver.Add(x[i][j] == x[j][i])

        # constraint: match only once
        for i in range(num_order):
            solver.Add(sum(x[i][j] for j in range(num_order)) <= 1)
            
        # objective: maximise the total trading volume
        solver.Maximize(sum(sum(mat_volume[i][j] * x[i][j] / 2 for j in range(num_order)) for i in range(num_order)))

        # solve
        dts = datetime.now()
        status = solver.Solve()
        dte = datetime.now()
        tm = round((dte - dts).seconds + (dte - dts).microseconds / (10 ** 6), 3)
        print("trading model solving time:  {} s".format(tm), '\n')

        # case 1: optimal
        self.list_match = []
        if status == pywraplp.Solver.OPTIMAL:
            print("solution:")
            obj_ = solver.Objective().Value()
            print("objective value:  {}".format(round(obj_)))
            x_ = [[x[i][j].solution_value() for j in range(num_order)] for i in range(num_order)]

            # result
            for i in range(num_order):
                for j in range(num_order):
                    if j > i and x_[i][j] > 0.9:
                        self.list_match.append((i, j))
                        print("order {} matches {} with trading volume {}".format(i, j, mat_volume[i][j]))
            print()

        # case 2: infeasible
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Ineasible!")

        # case 3: others
        else:
            raise Exception("Unexpected status: {}!".format(status))
