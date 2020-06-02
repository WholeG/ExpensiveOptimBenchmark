import numpy as np

from .IDONE import IDONE_minimize
from ..utils import Monitor

def optimize_IDONE(problem, max_evals, model='advanced'):
    d = problem.dims()
    lb = problem.lbs()
    ub = problem.ubs()

    if not all(problem.vartype() == 'int'):
        raise ValueError(f'Variable of type {vartype} supported by IDONE.')
    
    x0 = np.round(np.random.rand(d)*(ub-lb) + lb)

    mon = Monitor()
    def f(x):
        mon.commit_start_eval()
        r = problem.evaluate(x)
        mon.commit_end_eval(r)
        return r
    
    solX, solY, model, logfile = IDONE_minimize(f, x0, lb, ub, max_evals)

    return solX, solY, mon