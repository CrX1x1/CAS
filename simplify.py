#flip off TI for having a dumb naming schema for modules, all caps smh
try:
    from ast_test import *
except ImportError:
    from AST_TEST import *
def simplify(node):
    if node is None:
        return None
    #recurse to down first
    if node.left:
        node.left = simplify(node.left)
    if node.right:
        node.right = simplify(node.right)
    #crunch the simple ass numbers together
    if node.op == "+" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val + node.right.val)
    if node.op == "-" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val - node.right.val)
    if node.op == "*" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val * node.right.val)
    if node.op == "/" and node.left.op == "Num" and node.right.op == "Num":
        if node.right.val == 0:
            raise ZeroDivisionError("Sorry, no dividing by zero, buckaroo")
        return Node("Num", val=node.left.val / node.right.val)
    if node.op == "^" and node.left.op == "Num" and node.right.op == "Num":
        return Node("Num", val=node.left.val ** node.right.val)
    #exponent rules now
    if node.op == "^" and node.right.op == "Num" and node.right.val == 0:
        return Node("Num", val=1)
    if node.op == "^" and node.right.op == "Num" and node.right.val == 1:
        return node.left
    if node.op == "^" and node.left.op == "Num" and node.left.val == 0:
        return Node("Num", val=0)
    if node.op == "^" and node.left.op == "Num" and node.left.val == 1:
        return Node("Num", val=1)
    
    # identity rules, ez stuff
    # if 0+x, return x
    if node.op == "+" and node.left.op == "Num" and node.left.val == 0:
        return node.right
    #if 0-x, return -x
    if node.op == "-" and node.left.op == "Num" and node.left.val == 0:
        return Node("neg", left=node.right)
    # if x+0 or x-0, return x
    if (node.op == "+" or node.op == "-") and node.right.op == "Num" and node.right.val == 0:
        return node.left
    #if x*1 or x/1, return x
    if node.op == "*" and node.left.op == "Num" and node.left.val == 1:
        return node.right
    
    if node.op == "*" and node.right.op == "Num" and node.right.val == 1:
        return node.left

    if node.op == "/" and node.right.op == "Num" and node.right.val == 1:
        return node.left
    
    if node.op == "*" and (node.left.op == "Num" and node.left.val == 0 or node.right.op == "Num" and node.right.val == 0):
        return Node("Num", val=0)
    #negation rules
    if node.op == "neg" and node.left.op == "Num":
        return Node("Num", val=-float(node.left.val))
    if node.op == "neg" and node.left.op == "neg":
        return node.left.left
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
        return (1, None)
    if node.op == "Num":
        return (node.val, None)
    if node.op == "Var":
        return (1, node)
    if node.op == "neg":
        coeff, rest = get_coeff_and_rest(node.left)
        return (-coeff, rest)
    if node.op == "*":
        if node.left and node.left.op == "Num":
            coeff, rest = get_coeff_and_rest(node.right)
            return (node.left.val * coeff, rest)
        if node.right and node.right.op == "Num":
            coeff, rest = get_coeff_and_rest(node.left)
            return (node.right.val * coeff, rest)
    return (1, node)
def term_key(node):
    if node is None:
        return "1"
    if node.op == "Num":
        return "1"
    if node.op == "Var":
        return node.val
    if node.op == "neg":
        return "neg(" + term_key(node.left) + ")"
    if node.op == "*":
        left = term_key(node.left)
        right = term_key(node.right)
        return "*".join(sorted([left, right]))
    if node.op == "Funct":
        return node.val + "(" + term_key(node.left) + ")"
    return str(node) #just in case
def make_term_node(coeff, rest):
    if rest is None:
        return Node("Num", val=coeff)
    if coeff == 1:
        return rest
    if coeff == -1:
        return Node("neg", left=rest)
    return Node("*", left=Node("Num", val=coeff), right=rest)
def combine_like_terms(node):
    if node is None:
        return None
    flat_term = flatten(node)
    terms = {}
    constant = 0.0

    for t in flat_term:
        coeff, rest = get_coeff_and_rest(t)
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
        if coeff != 0:
            combined.append(make_term_node(coeff, rest))
        combined.sort(key=term_key)
    if constant != 0 or not combined:
        combined.append(Node("Num", val=constant))
    if not combined:
        return Node("Num", val=0)
    result = combined[0]
    for t in combined[1:]:
        result = Node("+", left=result, right=t)
    return result
# need to flatten so it actually combines like terms, found bug and asked AI, lol
def flatten(node, acc=None, sign=1.0):
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
    elif sign == -1.0:
        acc.append(Node("*", left=Node("Num", val=-1.0), right=node))
    else:
        acc.append(node)
    return acc

#please, for the love of god, stop importing random shit, autocomplete
#test
#print(simplify(Parser(tokenize("2+3*4")).parse()))
#print(simplify(Parser(tokenize("x+0")).parse()))
#print(simplify(Parser(tokenize("1*x")).parse()))
#print(simplify(Parser(tokenize("5382*x*0")).parse()))
#print(simplify(Parser(tokenize("(2+3)*x+0")).parse()))
