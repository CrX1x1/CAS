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
    combined = simplify(Node("+", left=lhs, right=Node("*", left=Node("Num", val=Frac(-1)), right=rhs)))
    coeffs = poly_coeffs(combined, var)
    if coeffs is None:
        raise ValueError("not a polynomial or has extra var: %s" % combined)
    return coeffs
def solve(equ, var="x"):
    lhs, rhs = parse_eq(equ)
    coeffs = isolate(var, lhs, rhs)
    return solve_poly(coeffs)
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
    root = root if isinstance(root, Frac) else Frac(root)
    n = len(coeffs)
    if n < 2:
        return [], coeffs[0] if coeffs else Frac(0)
    new_coeffs = [Frac(0)] * (n - 1)
    new_coeffs[0] = coeffs[0] if isinstance(coeffs[0], Frac) else Frac(coeffs[0])
    for i in range(1, n - 1):
        new_coeffs[i] = (coeffs[i] if isinstance(coeffs[i], Frac) else Frac(coeffs[i])) + new_coeffs[i - 1] * root
    remainder = (coeffs[-1] if isinstance(coeffs[-1], Frac) else Frac(coeffs[-1])) + new_coeffs[-1] * root
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

    if discr < Frac(0):
        return []
    denom = Frac(2) * a
    neg_b = Frac(-1) * b
    surd = Surd(1, discr)
    root1 = Node("/", left=Node("+", left=Node("Num", val=neg_b), right=Node("Num", val=surd)), right=Node("Num", val=denom))
    root2 = Node("/", left=Node("-", left=Node("Num", val=neg_b), right=Node("Num", val=surd)), right=Node("Num", val=denom))
    return [root1, root2]
def solve_poly(coeffs):
    #coerce to frac
    if not isinstance(coeffs, list):
        raise TypeError("read the damn code before running, bro \nput the coefficients in a damn list")
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
def factor_poly(coeffs):
    #coerce to frac
    coeffs = [c if isinstance(c, Frac) else Frac(c) for c in coeffs]
    while coeffs and coeffs[0] == Frac(0):
        coeffs.pop(0)
    if len(coeffs) <= 1:
        return Frac(coeffs[0]) if len(coeffs) == 1 else Frac(0)

    factors = []
    def _gcd(a, b):
        a, b = abs(int(a)), abs(int(b))
        while b:
            a, b = b, a % b
        return a or 1
    all_int = True
    nums = []
    for c in coeffs:
        if not isinstance(c, Frac):
            all_int = False
            break
        nums.append(c.numerator)
    cont = Frac(1)
    if all_int and nums:
        g = abs(nums[0])
        for n in nums[1:]:
            g = _gcd(g, n)
            if g == 1:
                break
        cont = Frac(g)
        if cont != Frac(1):
            coeffs = [c / cont for c in coeffs]
            factors.append([cont])
    # deg 1 or 0
    if len(coeffs) <= 2:
        factors.append(coeffs)
        return factors
    # deg 2
    if len(coeffs) == 3:
        a, b, c = coeffs
        discr = b*b - Frac(4) * a * c
        if discr < Frac(0):
            factors.append(coeffs)
            return factors
        s = Surd(1, discr)
        if s.radicand == Frac(1):
            r1 = (-b + s.coeff) / (Frac(2) * a)
            r2 = (-b - s.coeff) / (Frac(2) * a)
            factors.append([Frac(1), -r1])
            factors.append([Frac(1), -r2])
            return factors
        factors.append(coeffs)
        return factors
    # deg 3 or higher
    def _divisors(n):
        val = abs(int(n.numerator if hasattr(n, 'numerator') else n))
        if val == 0:
            return [1]
        return [i for i in range(1, val + 1) if val % i == 0]
    def possible_roots(coeffs):
        lead = coeffs[0]
        const = coeffs[-1]
        candidates = []
        for p in _divisors(const):
            for q in _divisors(lead):
                candidates.append(Frac(p, q))
                candidates.append(Frac(-p, q))
        unique_candidates = list(dict.fromkeys(candidates))
        return unique_candidates
    candidates = possible_roots(coeffs)
    for root in candidates:
        quot, rem = synthetic_division(coeffs, root)
        if rem == Frac(0):
            factors.append([Frac(1), -root])
            factors.extend(factor_poly(quot))
            return factors
    #irreducible
    factors.append(coeffs)
    return factors