import time
import gc

# Shims for MicroPython-specific time and memory functions so it runs on standard Python 3
if not hasattr(time, 'ticks_ms'):
    time.ticks_ms = lambda: int(time.perf_counter() * 1000)
if not hasattr(time, 'ticks_diff'):
    time.ticks_diff = lambda t1, t2: t1 - t2

if not hasattr(gc, 'mem_free'):
    gc.mem_free = lambda: 0  # Standard Python doesn't have a direct mem_free() heap counter

asdf = time.ticks_ms()

try:
    from ast_test import *
    from simplify import *
except ImportError:
    from AST_TEST import *
    from SIMPLIFY import *


TESTS = [
    (
        "Nested cancellation",
        "(x + y)*(x - y) - x*x + y*y"
    ),
    (
        "Nested negative distribution",
        "a - (b - (c - (d - e)))"
    ),
    (
        "Commutative multiplication",
        "2*sin(x)*cos(x) + 3*cos(x)*sin(x) - 5*sin(x)*cos(x)"
    ),
    (
        "Polynomial identity",
        "(x + y + z)^2 - x^2 - y^2 - z^2 - 2*x*y - 2*x*z - 2*y*z"
    ),
    (
        "Large Cartesian expansion",
        "(a+b+c+d+e)*(f+g+h+i+j)*(k+l+m+n+o)"
    ),
    (
        "Six-factor polynomial",
        "(x + 1)*(x + 2)*(x + 3)*(x + 4)*(x + 5)*(x + 6)"
    ),
    (
        "Trig coefficient combination",
        "3*(sin(x) + cos(x)) - 2*sin(x)"
    ),
    (
        "Nested distribution",
        "2*(3*(x + 2) - 4*(x - 1))"
    ),
    (
        "Zero multiplication",
        "0*(x + y + z)"
    ),
    (
        "Original mixed stress test",
        "-2*(3*x - 4) + 5 - x*x + sin(x)*2 + 10 - 4*x + 3*(x*x + 1) - 7"
    ),
    (
        "trig functions",
        "sin(x) + cos(x) + tan(x)"
    )
]


def run_test(name, expr):
    gc.collect()
    mem_before = gc.mem_free()

    print("\nTEST: %s" % name)
    print("Expression: %s" % expr)

    try:
        parsed = Parser(tokenize(expr)).parse()
        result = simplify(parsed)
        print("Result: %s" % str(result))

        # Test simplifier idempotence
        second = simplify(result)
        print("Second pass: %s" % str(second))
        print("Idempotent: %s" % (str(result) == str(second)))

    except Exception as e:
        print("ERROR: %s" % str(e))

    gc.collect()
    mem_after = gc.mem_free()

    print("Net heap consumed: %d bytes" % (mem_before - mem_after))
    print("Free heap: %d bytes" % mem_after)
    input("Press Enter to continue...")


def benchmark():
    gc.collect()
    print("INITIAL FREE HEAP: %d bytes" % gc.mem_free())

    for i, test in enumerate(TESTS):
        print("\n========== TRIAL %d ==========" % (i + 1))
        run_test(test[0], test[1])

    print("\n========== COMPLETE ==========")
    print("Total time: %d ms" % time.ticks_diff(time.ticks_ms(), asdf))
    print("Final free heap: %d bytes" % gc.mem_free())
    input("Press Enter to exit...")

if __name__ == "__main__":
    benchmark()