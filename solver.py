import math


try:
    from ast_test import *
    from simplify import *
except ImportError:
    from AST_TEST import * #again with calculator nonsense
    from SIMPLIFY import *
def parse_eq(equ):
    if "=" not in equ:
        #assuming it's an expr and not equ, pass normally
        #even tho i had a check in solve() lol
        return Parser(tokenize(equ)).parse(), None
    parts = equ.split("=")
    if len(parts) != 2:
        raise ValueError("wtf is this bro: %s? It's not a valid equation, dumbass" % equ)

    lhs = Parser(tokenize(parts[0])).parse()
    rhs = Parser(tokenize(parts[1])).parse()
    return lhs, rhs
def isolate(var, lhs, rhs):
    combined = Node("-", left=lhs, right=rhs)

    simplified = simplify(combined)
    flat = flatten(simplified)
    coeff = Frac(0)
    constant = Frac(0)
    for term in flat:
        c, rest = get_coeff_and_rest(term)
        if rest is None:
            constant += c
        elif rest.op == "Var" and rest.val == var:
            coeff += c
        else:
            raise ValueError("yeah, hell no, i'm not doing all that: %s" % rest)
    if coeff == 0:
        raise ValueError("uhh what happened to the variable, help")
    return Node("Num", val=Frac(Frac(-1) * constant, coeff))
def solve(equ, var="x"):
    if "=" not in equ:
        raise ValueError("This thing ain't an equation, did you expect me to materialize it into existence?")
    lhs, rhs = parse_eq(equ)
    if rhs is None:
        raise ValueError("Funny, you got a secret message error, must've been a bug")
    return simplify(isolate(var, lhs, rhs))
#damn calculator doesn't have math.gcd, thanks, AI
def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)
def gcd_list(nums):
    g = abs(int(nums[0]))
    for n in nums[1:]:
        g = gcd(g, abs(int(n)))
        if g == 1:
            return 1
    return g
def synthetic_division(coeffs, root):
    n = len(coeffs)
    new_coeffs = [0] * (n - 1)
    new_coeffs[0] = coeffs[0]
    for i in range(1, n - 1):
        new_coeffs[i] = coeffs[i] + new_coeffs[i - 1] * root
    remainder = coeffs[-1] + new_coeffs[-1] * root
    return new_coeffs, remainder
def possible_roots(coeffs):
    def factors(n):
        if isinstance(n, Frac):
            n = n.numerator
        n=abs(int(n))
        return [i for i in range(1, n + 1) if n % i == 0]
    lead_coeff = coeffs[0]
    constant_term = coeffs[-1]
    if isinstance(lead_coeff, Frac): lead_coeff = lead_coeff.numerator
    if isinstance(constant_term, Frac): constant_term = constant_term.numerator
    possible = []
    for p in factors(constant_term):
        for q in factors(lead_coeff):
            possible.append(Frac(p,q))
            possible.append(Frac(-p,q))
    return list(set(possible))
def quadratic_formula(a, b, c):
    a=a if isinstance(a, Frac) else Frac(a)
    b=b if isinstance(b, Frac) else Frac(b)
    c=c if isinstance(c, Frac) else Frac(c)
    if a == Frac(0):
        if b == Frac(0):
            return [] # linear smh
        return [Frac(-1)*c / b]
    discr = b**Frac(2) - Frac(4)*a*c

    if discr.numerator < 0 or isinstance(discr, Frac) and discr.denominator != 1 and discr.numerator < 0:
        return []

    raw_discr_val = discr.numerator / discr.denominator
    root_val = int(math.sqrt(int(raw_discr_val)))
    if root_val * root_val == raw_discr_val:
        s = Frac(root_val)
        return [
            (Frac(-1) * b + s) / (Frac(2) * a),
            (Frac(-1) * b - s) / (Frac(2) * a)
        ]
    else:
        # If it's an imperfect square, wrap it or handle the radical exactness
        raise ValueError("Non-perfect square discriminants need radical simplification, you animal")
def solve_poly(coeffs):
    #coerce to frac
    coeffs = [c if isinstance(c, Frac) else Frac(c) for c in coeffs]

    while len(coeffs) > 1 and coeffs[0] == 0:
        coeffs = coeffs[1:]
    if not coeffs:
        return []

    #strip gcf
    g = gcd_list(coeffs)
    if g > 1:
        coeffs = [c // g for c in coeffs]
    degree = len(coeffs) - 1
    if degree == 0:
        return [] 
    #linear
    if degree == 1:
        a, b = coeffs
        if a == Frac(0):
            return []
        return [Frac(-1)*b / a]
    #quadratic
    if degree == 2:
        a, b, c = coeffs
        return quadratic_formula(a, b, c)
    #cubic and higher, use rational root theorem and synthetic division
    candidates = possible_roots(coeffs)
    for root in candidates:
        new_coeffs, remainder = synthetic_division(coeffs, root)
        if remainder == Frac(0): #screw floating point errors
            return [root] + solve_poly(new_coeffs)

    return []  # no rational roots found