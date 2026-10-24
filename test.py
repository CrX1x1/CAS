from time import *
asdf = ticks_ms()
try:
    from ast_test import *
    from simplify import *
except ImportError:
    from AST_TEST import *
    from SIMPLIFY import *
import gc

def benchmark():
    gc.collect()
    mem_before = gc.mem_free()
    
    # Run a beefy expression to test heap pressure
    expr = "-2 * (3*x - 4) + 5 - x*x + sin(x) * 2 + 10 - 4*x + 3*(x*x + 1) - 7"
    parsed = Parser(tokenize(expr)).parse()
    result = str(simplify(parsed))
    
    gc.collect()
    mem_after = gc.mem_free()
    mem_used = mem_before - mem_after
    
    print("STRESS TEST TRIAL 1")
    print("Result: %s" % result)
    print("Heap memory consumed: %d bytes" % mem_used)
    print("Free heap remaining: %d bytes" % gc.mem_free())
benchmark()
print("time taken: " + str(ticks_diff(ticks_ms(), asdf)) + " ms")