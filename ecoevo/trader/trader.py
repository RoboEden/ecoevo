
from datetime import datetime
from typing import List, Dict, Tuple
 
from ortools.linear_solver import pywraplp


def trade(num_offer: int, mat_if_match: List[List[bool]], mat_volume: List[List[int]]) -> Dict[Tuple[int, int], int]:
    """
    IP Model for automated trade matching

    :param num_offer:  the number of offers
    :param mat_if_match:  available matching matrix
    :param mat_volume:  trading volume matrix

    :return: dict_match:  result dictionary, (offer, offer) -> trading volume
    """

    solver = pywraplp.Solver(name='location', problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        
    # variable: if choose a match
    x = [[solver.BoolVar('x_{}_{}'.format(i, j)) for j in range(num_offer)] for i in range(num_offer)]

    # constraint: validation
    for i in range(num_offer):
        for j in range(num_offer):
            solver.Add(x[i][j] <= mat_if_match[i][j])

    # constraint: symmetry
    for i in range(num_offer):
        for j in range(num_offer):
            solver.Add(x[i][j] == x[j][i])

    # constraint: match only once
    for i in range(num_offer):
        solver.Add(sum(x[i][j] for j in range(num_offer)) <= 1)
        
    # objective: maximise the total trading volume
    solver.Maximize(sum(sum(mat_volume[i][j] * x[i][j] / 2 for j in range(num_offer)) for i in range(num_offer)))

    # solve
    dts = datetime.now()
    status = solver.Solve()
    dte = datetime.now()
    tm = round((dte - dts).seconds + (dte - dts).microseconds / (10 ** 6), 3)
    print("trading model solving time:  {} s".format(tm), '\n')

    # case 1: optimal
    dict_match = {}
    if status == pywraplp.Solver.OPTIMAL:
        print("solution:")
        obj_ = solver.Objective().Value()
        print("objective value:  {}".format(round(obj_)))
        x_ = [[x[i][j].solution_value() for j in range(num_offer)] for i in range(num_offer)]

        # result
        for i in range(num_offer):
            for j in range(num_offer):
                if j > i and x_[i][j] > 0.9:
                    dict_match[i, j] = mat_volume[i][j]
                    print("offer {} matches {} with trading volume {}".format(i, j, dict_match[i, j]))
        print()

    # case 2: infeasible
    elif status == pywraplp.Solver.INFEASIBLE:
        raise Exception("Ineasible!")

    # case 3: others
    else:
        raise Exception("Unexpected status: {}!".format(status))

    return dict_match
