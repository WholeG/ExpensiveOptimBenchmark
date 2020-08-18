import numpy as np

from .IDONE import IDONE_minimize
from ..utils import Monitor, Binarizer

def optimize_IDONE(problem, max_evals, rand_evals=5, model='advanced', binarize_categorical=False, binarize_int=False, sampling = None, enable_scaling=False, log=None, exploration_prob='normal', idone_log=False):
    d = problem.dims()
    lb = problem.lbs()
    ub = problem.ubs()

    supported = (np.logical_or(problem.vartype() == 'int', problem.vartype() == 'cat'))

    if not (supported).all():
        raise ValueError(f'Variable of types {np.unique(problem.vartype()[np.logical_not(supported)])} are not supported by IDONE.')
    
    x0 = np.round(np.random.rand(d)*(ub-lb) + lb)

    # Don't enable binarization if there is nothing to binarize.
    binarize_categorical = binarize_categorical and (problem.vartype() == 'cat').any()
    binarize_int = binarize_int and (problem.vartype() == 'int').any()

    if binarize_categorical or binarize_int:
        if binarize_categorical and binarize_int:
            b = Binarizer(problem.vartype() == 'cat' or problem.vartype() == 'int', lb, ub)
        elif binarize_categorical:
            b = Binarizer(problem.vartype() == 'cat', lb, ub)
        else:
            b = Binarizer(problem.vartype() == 'int', lb, ub)
        x0 = b.binarize(x0)
        # Get new bounds.
        lb = b.lbs()
        ub = b.ubs()

    # Compute exploration probability
    probability_values = {'normal': 1/d, 
                          'larger': 1-(0.01)**(1/d)
                            }
    if exploration_prob in probability_values:
        prob = probability_values.get(exploration_prob)
    else:
        raise ValueError(f'Can not find any probability value matching {exploration_prob}. Create a new value or change to an existing one: {probability_values.keys()}')


    mon = Monitor(f"IDONE/{model}{'/scaled' if enable_scaling else ''}{'/binarized' if binarize_categorical or binarize_int else ''}{'/'+sampling if sampling != 'none' else ''}{'/'+exploration_prob}", problem, log=log)
    def f(x):
        mon.commit_start_eval()
        if binarize_categorical or binarize_int:
            xalt = b.unbinarize(x)
        else:
            xalt = x
        r = problem.evaluate(xalt)
        mon.commit_end_eval(xalt, r)
        return r
    
    mon.start()
    solX, solY, model, logfile = IDONE_minimize(f, x0, lb, ub, max_evals, rand_evals=rand_evals, enable_scaling=enable_scaling, model_type=model, sampling = sampling, exploration_prob=prob, log=idone_log)
    mon.end()

    return solX, solY, mon