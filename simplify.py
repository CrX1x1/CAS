#flip off TI for having a dumb naming schema for modules, all caps smh
try:
    from ast_test import *
except ImportError:
    from AST_TEST import *
from math import *

sin_table = {
    (0,1): Frac(0),
    (1,6): Frac(1,2),
    (1,4): Surd(Frac(1,2),2),
    (1,3): Surd(Frac(1,3),2), #dammit, no Surd in Frac
    (1,2): Frac(1)
}
cos_table = {
    (0,1): Frac(1),
    (1,6): Surd(Frac(1,3),2),
    (1,4): Surd(Frac(1,2),2),
    (1,3): Frac(1,2),
    (1,2): Frac(0)
}
#helper checks
def is_frac_zero(v):
    return isinstance(v, Frac) and v == Frac(0)
def is_frac_one(v):
    return isinstance(v, Frac) and v == Frac(1)

def collect_products(node):
    if node.op == "Num":
        if isinstance(node.val, Frac):
            return node.val, {}
    if node.op == "Var":
        return Frac(1), {node.val: 1}
        #return None
    if node.op == "*":
        left = collect_products(node.left)
        right = collect_products(node.right)
        if left is None or right is None:
            return None
        coeff = left[0] * right[0]
        vdict = dict(left[1])
        for k, v in right[1].items():
            vdict[k] = vdict.get(k, 0) + v
        return coeff, vdict
    if node.op == "^":
        if node.left.op == "Var" and node.right.op == "Num" and isinstance(node.right.val, Frac) and node.right.val.denominator == 1 and node.right.val.numerator >= 0:
            return Frac(1), {node.left.val: node.right.val.numerator}
        return None
    if node.op == "neg":
        inner = collect_products(node.left)
        if inner is None:
            return None
        return -inner[0], inner[1]
    return None
def reduce_pi_frac(p, q):
    if q < 0:
        p,q = -p,-q
    p=p%(2*q)
    if p < 0:
        p += 2*q
    p2 = p*2

    if p2 <= q:
        return (p,q), 1, 1
    elif p2 <= 2*q:
        return (q-p,q), 1, -1
    elif p2 <= 3*q:
        return (p-q,q), -1, -1
    else:
        return (2*q-p,q), -1, 1

def match_pi_frac(node):
    if node is None:
        return None
    if node.op == "Const" and node.val == "pi":
        return (1, 1)

    def extract(node):
        if node.op == "Const" and node.val == "pi":
            return Frac(1)
        if node.op == "Num":
            return node.val if isinstance(node.val, Frac) else Frac(node.val)
        if node.op == "neg":
            val = extract(node.left)
            return -val if val is not None else None
        if node.op in ("*", "/"):
            left = extract(node.left)
            right = extract(node.right)
            if left is not None and right is not None:
                if node.op == "*":
                    return left * right
                else:
                    return left / right
        return None
    coeff = extract(node)
    if coeff is None:
        return None
    if isinstance(coeff, Frac):
        return (coeff.numerator, coeff.denominator)
    return None
def exact_trig(funct_name, node):
    key = match_pi_frac(node)
    if key is None:
        return None
    p,q = key
    (rp, rq), sin_sign, cos_sign = reduce_pi_frac(p, q)
    g=gcd(rp, rq)
    rp//=g
    rq//=g

    table = sin_table if funct_name == "sin" else cos_table if funct_name == "cos" else None
    sign = sin_sign if funct_name == "sin" else cos_sign if funct_name == "cos" else 1
    if funct_name == "sin":
        table, sign = sin_table, sin_sign
    elif funct_name == "cos":
        table, sign = cos_table, cos_sign
    elif funct_name == "tan":
        if (rp, rq) == (1, 2): #what kinda of math is this, tan(pi/2) = undefined
            return None
        s = exact_trig("sin", node)
        c = exact_trig("cos", node)
        if s is None or c is None:
            return None
        if c.val == Frac(0):
            return None
        return Node("Num", val=s.val / c.val)
    lookup = (rp, rq)

    if lookup not in table:
        return None

    val = table[lookup]
    if sign == -1:
        if isinstance(val, Surd):
            val = Surd(-val.coeff, val.radicand)
        else:
            val = -val
            
    return Node("Num", val=val)
def simplify(node):
    if node is None:
        return None
    if isinstance(node, Frac):
        return node
    #recurse to down first
    if node.left:
        node.left = simplify(node.left)
    if node.right:
        node.right = simplify(node.right)
    exact_val = numeric_fraction(node)

    #crunch the simple ass numbers together
    if node.op == "+" and node.left.op == "Num" and node.right.op == "Num":
        try:
            result = node.left.val + node.right.val
            if result is not NotImplemented:
                return Node("Num", val=result)
        except TypeError:
            pass
    if node.op == "-" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val - node.right.val)
    if node.op == "*" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val * node.right.val)
    if node.op == "/" and node.left.op == "Num" and node.right.op == "Num":
        if node.right.val == Frac(0):
            raise ZeroDivisionError("Sorry, no dividing by zero, buckaroo")
        return Node("Num", val=node.left.val / node.right.val)
    if node.op == "^" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val ** node.right.val)
    #symbolic now?
    if node.op == "Funct" and node.val == "sqrt":
        if node.left.op == "Num":
            if node.left.val < Frac(0):
                raise ValueError("This number is like your dad, it doesn't exist")
            return Node("Num", val=Surd(1, node.left.val))
    if node.op == "Funct" and node.val in ("sin", "cos", "tan"):
        exact = exact_trig(node.val, node.left)
        if exact is not None:
            return exact
    if node.op == "Funct" and node.val in ("csc", "sec", "cot"):
        arg = node.left
        if node.val == "csc":
            s = exact_trig("sin", arg)
            if s is None or s.val == Frac(0):
                return node
            return Node("Num", val=Frac(1) / s.val)
        if node.val == "sec":
            c = exact_trig("cos", arg)
            if c is None or c.val == Frac(0):
                return node
            return Node("Num", val=Frac(1) / c.val)
        if node.val == "cot":
            s = exact_trig("sin", arg)
            c = exact_trig("cos", arg)
            if s is None or c is None or s.val == Frac(0):
                return node
            return Node("Num", val=c.val / s.val)
    if node.op == "Funct":
        if node.left.op == "Num":
            if node.left.val < Frac(0):
                raise ValueError("This number is like your dad, it doesn't exist")
            return Node("Num", val=eval(node.op + "(" + str(node.left.val) + ")"))
        
    #exponent rules now
    if node.op == "^" and node.right.op == "Num" and is_frac_zero(node.right.val):
        return Node("Num", val=1)
    if node.op == "^" and node.right.op == "Num" and is_frac_one(node.right.val):
        return node.left
    if node.op == "^" and node.left.op == "Num" and is_frac_zero(node.left.val):
        return Node("Num", val=Frac(0))
    if node.op == "^" and node.left.op == "Num" and is_frac_one(node.left.val):
        return Node("Num", val=1)
    
    # identity rules, ez stuff
    # if 0+x, return x
    if node.op == "+" and node.left.op == "Num" and is_frac_zero(node.left.val):
        return node.right
    #if 0-x, return -x
    if node.op == "-" and node.left.op == "Num" and is_frac_zero(node.left.val):
        return Node("neg", left=node.right)
    # if x+0 or x-0, return x
    if (node.op == "+" or node.op == "-") and node.right.op == "Num" and is_frac_zero(node.right.val):
        return node.left
    #if x*1 or x/1, return x
    if node.op == "*" and node.left.op == "Num" and is_frac_one(node.left.val):
        return node.right
    
    if node.op == "*" and node.right.op == "Num" and is_frac_one(node.right.val):
        return node.left

    if node.op == "/" and node.right.op == "Num" and is_frac_one(node.right.val):
        return node.left
    
    if node.op == "*" and (node.left.op == "Num" and is_frac_zero(node.left.val) or node.right.op == "Num" and is_frac_zero(node.right.val)):
        return Node("Num", val=Frac(0))
    #negation rules
    if node.op == "neg" and node.left.op == "Num":
        return Node("Num", val=-node.left.val)
    if node.op == "neg" and node.left.op == "neg":
        return node.left.left

    # power product rule: a^m * a^n = a^(m+n)
    if node.op == "*":
        left, right = node.left, node.right
        # Thanks, AI
        # x^a * x^b  =  x^(a+b)
        if (left.op == "^" and right.op == "^" and
            left.left.op == "Var" and right.left.op == "Var" and
            left.left.val == right.left.val and
            left.right.op == "Num" and right.right.op == "Num"):
            new_exp = left.right.val + right.right.val          # both are Fracs
            return Node("^", left=left.left, right=Node("Num", val=new_exp))

        # x^a * x  =  x^(a+1)
        if (left.op == "^" and right.op == "Var" and
            left.left.op == "Var" and left.left.val == right.val and
            left.right.op == "Num"):
            new_exp = left.right.val + Frac(1)
            return Node("^", left=left.left, right=Node("Num", val=new_exp))

        # x * x^a  =  x^(a+1)
        if (right.op == "^" and left.op == "Var" and
            right.left.op == "Var" and right.left.val == left.val and
            right.right.op == "Num"):
            new_exp = right.right.val + Frac(1)
            return Node("^", left=right.left, right=Node("Num", val=new_exp))
        if left.op == "Var" and right.op == "Var" and left.val == right.val:
            return Node("^", left=left, right=Node("Num", val=Frac(2)))
    if node.op == "/":
        num, den = simplify(node.left), simplify(node.right)
        #assuming variable is x for testing purposes
        num_coeffs = poly_coeffs(num)
        den_coeffs = poly_coeffs(den)
        if num_coeffs is not None and den_coeffs is not None:
            g = poly_gcd(num_coeffs, den_coeffs)
            num_coeffs, _ = poly_divmod(num_coeffs, g)
            den_coeffs, _ = poly_divmod(den_coeffs, g)
            num = poly_to_node(num_coeffs)
            den = poly_to_node(den_coeffs)
            #return numerator only if denominator is 1
            if den_coeffs == [Frac(1)]:
                return num
            node = Node("/", left=num, right=den)
    node = expand(node)
    if node.op in ("+", "-"):
        node = combine_like_terms(node)
    return node
def expand(node):
    if node is None:
        return None
    #expand children first
    node.left = expand(node.left)
    node.right = expand(node.right)
    if node.op == "^":
        if node.left.op in ("+", "-") and node.right.op == "Num" and isinstance(node.right.val, Frac) and node.right.val.denominator == 1 and node.right.val.numerator >= 0:
            n = node.right.val.numerator
            base = node.left
            if n == 1:
                return base
            expr = base
            for _ in range(n - 1):
                expr = expand(Node("*", left=expr, right=base))
            return expr
    # multiply by sum/difference
    if node.op == "*":
        #case 1: a*(b+c) = a*b + a*c
        if node.right and node.right.op in ("+", "-"):
            op = node.right.op
            a = node.left
            b = node.right.left
            c = node.right.right
            return expand(Node(op, left=Node("*", left=a, right=b), right=Node("*", left=a, right=c)))
        #case 2: (a+b)*c = a*c + b*c
        if node.left and node.left.op in ("+", "-"):
            op = node.left.op
            a = node.left.left
            b = node.left.right
            c = node.right
            return expand(Node(op, left=Node("*", left=a, right=c), right=Node("*", left=b, right=c)))
    return node
def is_term(node):
    if node is None:
        return False
    if node.op in ("Num", "Var"):
        return True
    if node.op == "neg":
        return is_term(node.left)
    if node.op == "^":
        return is_term(node.left) and is_term(node.right)
    if node.op in ("*", "/"):
        return is_term(node.left) and is_term(node.right)
    if node.op == "Funct":
        return is_term(node.left)
    return False
def get_coeff_and_rest(node):
    if node is None:
        return (Frac(1), None)
    if isinstance(node, Frac):
        return (node, None)
    if node.op == "Num":
        if isinstance(node.val, Surd):
            pure = Surd(1, node.val.radicand) 
            return (node.val.coeff, Node("Num", val=pure))
        return (node.val, None)
    if node.op == "Var":
        return (Frac(1), node)
    if node.op == "neg":
        coeff, rest = get_coeff_and_rest(node.left)
        return (Frac(-coeff), rest)

    #new collect_products function
    collected = collect_products(node)
    if collected is not None:
        coeff, var_dict = collected
        if not var_dict:
            return (coeff, None)
        sorted_vars = sorted(var_dict.items())
        factors = []
        for var, power in sorted_vars:
            if power == 1:
                factors.append(Node("Var", val=var))
            else:
                factors.append(Node("^", left=Node("Var", val=var), right=Node("Num", val=Frac(power))))
        if not factors:
            return (coeff, None)
        node = factors[0]
        for factor in factors[1:]:
            node = Node("*", left=node, right=factor)
        return (coeff, node)
    # legacy code, just in case
    if node.op == "*":
        if node.left and node.left.op == "Num":
            coeff, rest = get_coeff_and_rest(node.right)
            return (node.left.val * coeff, rest)
        if node.right and node.right.op == "Num":
            coeff, rest = get_coeff_and_rest(node.left)
            return (node.right.val * coeff, rest)
    return (Frac(1), node)
def term_key(node):
    if node is None:
        return "1"
    if node.op == "Num":
        if isinstance(node.val, Surd):
            return "sqrt(%s)" % str(node.val.radicand)
        return "1"
    if node.op == "Var":
        return node.val
    if node.op == "neg":
        return "neg(" + term_key(node.left) + ")"
    if node.op == "*":
        factors = []
        def collect(n):
            if n.op == "*":
                collect(n.left)
                collect(n.right)
            else:
                factors.append(term_key(n))
        collect(node)
        factors.sort()
        return "*".join(factors)
        #just some old stuff just in case
        '''left = term_key(node.left)
        right = term_key(node.right)
        return "*".join(sorted([left, right]))
        '''
    if node.op == "^":
        base = term_key(node.left)
        if node.right.op == "Num":
            exp = str(node.right.val)
        else:
            exp = term_key(node.right)
        return base + "^" + exp
        #return term_key(node.left) + "^" + term_key(node.right)
    if node.op == "Funct":
        return node.val + "(" + term_key(node.left) + ")"
    return str(node) #just in case
def degree_key(node):
    if node is None or node.op == "Num":
        return 0
    if node.op == "Var":
        return 1
    if node.op == "^" and node.left.op == "Var" and node.right.op == "Num":
        return int(node.right.val)
    if node.op == "*":
        return degree_key(node.right)
    if node.op == "/":
        return degree_key(node.left)
    return 0
def poly_key(node):
    coeff, rest = get_coeff_and_rest(node)
    if rest is None:
        return ()
    collected = collect_products(rest) if rest else None
    if collected is None:
        return ()
    _, var_dict = collected
    sorted_items = sorted(var_dict.items())
    return tuple(var_dict[e] for e, _ in sorted_items)
def make_term_node(coeff, rest):
    if not isinstance(coeff, Frac):
        coeff = Frac(coeff)
    if rest is None:
        return Node("Num", val=coeff)
    if (rest.op == "Num" and isinstance(rest.val, Surd)) and rest.val.coeff == Frac(1):
        return Node("Num", val=Surd(coeff, rest.val.radicand))
    if coeff == Frac(1):
        return rest
    if coeff == Frac(-1):
        return Node("neg", left=rest)
    return Node("*", left=Node("Num", val=coeff), right=rest)
def combine_like_terms(node):
    if node is None:
        return None
    flat_term = flatten(node)
    terms = {}
    constant = Frac(0)

    for t in flat_term:
        coeff, rest = get_coeff_and_rest(t)
        key = term_key(rest)
        if rest is None:
            constant += coeff
        else:
            key = term_key(rest)
            if key in terms:
                old_coeff, old_rest = terms[key]
                terms[key] = (coeff+old_coeff, old_rest)
            else:
                terms[key] = (coeff, rest)
    combined = []
    for key, (coeff, rest) in terms.items():
        if coeff != Frac(0):
            combined.append(make_term_node(coeff, rest))
        combined.sort(key=poly_key, reverse=True)
    if constant != Frac(0) or not combined:
        combined.append(Node("Num", val=constant))
    if not combined:
        return Node("Num", val=Frac(0))
    result = combined[0]
    for t in combined[1:]:
        result = Node("+", left=result, right=t)
    return result
# need to flatten so it actually combines like terms, found bug and asked AI, lol
def flatten(node, acc=None, sign=Frac(1)):
    if acc is None:
        acc = []
    if node is None:
        return acc
    if node.op == "+":
        flatten(node.left, acc, sign)
        flatten(node.right, acc, sign)
    elif node.op == "-":
        flatten(node.left, acc, sign)
        flatten(node.right, acc, -sign)
    elif node.op == "Num":
        acc.append(Node("Num", val=sign * node.val))
    elif sign == Frac(-1):
            acc.append(Node("*", left=Node("Num", val=Frac(-1)), right=node))
    else:
        acc.append(node)
    return acc
def poly_coeffs(node, var="x"):
    flat = flatten(node)
    degrees = {}
    for term in flat:
        c, rest = get_coeff_and_rest(term)
        if rest is None:
            deg = 0
        elif rest.op == "Var" and rest.val == var:
            deg = 1
        elif rest.op == "^" and rest.left.op == "Var" and rest.left.val == var:
            deg = int(rest.right.val.numerator)
        else:
            return None #something that isn't non-negative int power of var, skip
        degrees[deg] = degrees.get(deg, Frac(0)) + c
    if not degrees:
        return [Frac(0)]
    max_degree = max(degrees)
    coeffs = [degrees.get(i, Frac(0)) for i in range(max_degree, -1, -1)]
    return coeffs
def poly_to_node(coeffs, var="x"):
    if not coeffs:
        return Node("Num", val=Frac(0))
    #highest degree term first
    n = len(coeffs) - 1
    result = None
    for i, c in enumerate(coeffs):
        deg = n - i
        if deg == 0:
            term = Node("Num", val=c)
        elif deg == 1:
            term = make_term_node(c, Node("Var", val=var))
        else:
            term = make_term_node(c, Node("^", left=Node("Var", val="x"), right=Node("Num", val=Frac(deg))))
        if result is None:
            result = term
        else:
            result = Node("+", left=result, right=term)
    return result if result is not None else Node("Num", val=Frac(0))
def factors_to_node(factors, var="x"):
    if not factors:
        return Node("Num", val=Frac(0))
    result = poly_to_node(factors[0], var)
    for factor in factors[1:]:
        result = Node("*", left=result, right=poly_to_node(factor, var))
    return result
def poly_divmod(num, den):
    while num and num[0] == Frac(0):
        num.pop(0)
    while den and den[0] == Frac(0):
        den.pop(0)
    if not den:
        raise ZeroDivisionError("division by zero polynomial")
    if len(num) < len(den):
        return [Frac(0)], num
    deg_num = len(num) - 1
    deg_den = len(den) - 1
    max_deg_diff = deg_num - deg_den
    quotient = [Frac(0)] * (max_deg_diff + 1)
    remainder = list(num)

    while len(remainder) >= len(den) and remainder and remainder[0] != Frac(0):
        deg_diff = len(remainder) - len(den)
        coeff = remainder[0] / den[0]
        idx = max_deg_diff - deg_diff
        quotient[idx] = coeff
        for i, factor in enumerate(den):
            remainder[i] -= coeff * factor
        while remainder and remainder[0] == Frac(0):
            remainder.pop(0)
    return quotient, remainder
def poly_gcd(a, b):
    while b and any(c != Frac(0) for c in b):
        _, r = poly_divmod(a, b)
        a, b = b, r
    # no more normalization, screw that
    while a and a[0] == Frac(0):
        a.pop(0)
    if not a:
        return [Frac(1)]
    #never mind
    lc = a[0]
    if lc != Frac(1):
        a = [c / lc for c in a]
    return a
#please, for the love of god, stop importing random shit, autocomplete
#test
#print(simplify(Parser(tokenize("2+3*4")).parse()))
#print(simplify(Parser(tokenize("x+0")).parse()))
#print(simplify(Parser(tokenize("1*x")).parse()))
#print(simplify(Parser(tokenize("5382*x*0")).parse()))
#print(simplify(Parser(tokenize("(2+3)*x+0")).parse()))
