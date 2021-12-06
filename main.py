import time
from distribute_challenge import compute_this

@compute_this()
def func(x):
    time.sleep(x)
    return x*x

out = func(2).run()
assert out == 4

