def evaluate(node, variables=None):
    if variables is None:
        variables = {}
    if node is None:
        return 0.0
    if node.op == "Num":
        return node.val
    if node.op == "Var":
        if node.val in variables:
            return variables[node.val]
        raise NameError("wtf is this: %s? It's not defined" % node.val)

    if node.op == "neg":
        return -evaluate(node.left, variables)
    if node.op == "Funct":
        import math
        arg_value = evaluate(node.left, variables)
        funct_mapping = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "sqrt": math.sqrt
        }
        if node.val in funct_mapping:
            return funct_mapping[node.val](arg_value)
        raise ValueError("wtf is this function: %s? It's not defined" % node.val)
    #now that those are out of the way, binary ops, assemble
    left_val = evaluate(node.left, variables)
    right_val = evaluate(node.right, variables)
    if node.op == "+":
        return left_val + right_val
    if node.op == "-":
        return left_val - right_val
    if node.op == "*":
        return left_val * right_val
    if node.op == "/":
        if right_val == 0:
            raise ZeroDivisionError("Sorry, no dividing by zero, buckaroo")
        return left_val / right_val
    if node.op == "^":
        return left_val ** right_val
    # now i dunno what the user is asking for, so go screw them
    raise ValueError("wtf is this bro: %s? "% node.op)
#test
#import ast_test as ast #python is a pain in the ass to import local files, so i have to rename it
#print(evaluate(ast.Parser(ast.tokenize("-2sin(3.5x)*-(4+1)")).parse(), {"x": 3}))
#print(evaluate(ast.Parser(ast.tokenize("-2sin(3.5x)*-(4+1)")).parse(), {"x": 6.7}))