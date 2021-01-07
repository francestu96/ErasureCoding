from consts import YEAR
from random import expovariate
import sys

def log(state, message):
    print(f'[time: {state.t/YEAR:.2f} local blocks: {sum(state.local_blocks)} remote blocks: {sum(state.remote_blocks)}] {message}', file=sys.stderr)

def get_true_len(array):
    res = 0
    for val in array:
        if val: res += 1
    return res
    
def exp_rv(mean):
    """Return an exponential random variable with the given mean."""
    return expovariate(1 / mean)