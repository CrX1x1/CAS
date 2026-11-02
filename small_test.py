from ast_test import *
from solver import *
from simplify import *

num = [Frac(3), Frac(0), Frac(-5), Frac(7), Frac(-9)]
den = [Frac(1), Frac(-1)]
print("gcd:", poly_gcd(num, den))
print("divmod:", poly_divmod(num, den))