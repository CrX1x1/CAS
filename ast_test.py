class Node:
    __slots__ = ("op", "left", "right", "val")
    def __init__(self, op, left=None, right=None, val=None):
        self.op = op
        self.left = left
        self.right = right
        self.val = val
    def __repr__(self):
        if self.val is not None:
            return "%s(%s, %s, %s)" % (self.op, self.val, self.left, self.right)
        return "%s(%s, %s)" % (self.op, self.left, self.right)
    def __str__(self):
        if self.op == "Num":
            return str(self.val)
        if self.op == "Var":
            return str(self.val)
        if self.op == "neg":
            return "-%s" % str(self.left)
        if self.op == "Funct":
            return "%s(%s)" % (self.val, str(self.left))
        if self.op in ("+", "-", "*", "/", "^"):
            return "(%s %s %s)" % (str(self.left), self.op, str(self.right))
def add(l, r): return Node("+", l, r)
def sub(l, r): return Node("-", l, r)
def mul(l, r): return Node("*", l, r)
def div(l, r): return Node("/", l, r)
def pow(l, r): return Node("^", l, r)
def Var(name): return Node("Var", val=name)
def Num(n): return Node("Num", val=n)

#test = mul(div(Num(4), Num(2)), Var("x"))
#print(test)  # Output should be this:  *(/(Num(4), Num(2)), Var(x))

def isalnum(s):
    for i in list(s):
        if not (i.isalpha() or i.isdigit()):
            return False
    return True

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def next_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    def parse(self):
        if not self.tokens:
            return None
        return self.expr()
    def expr(self): # addition and subtraction, lowest precedence
        node = self.term()
        while self.current_token is not None and self.current_token in "+-":
            op = self.current_token
            self.next_token()
            node = Node(op, left=node, right=self.term())
        return node
    def term(self): # multiplication and division, higher precedence
        node = self.unary()
        while self.current_token is not None and self.current_token in "*/":
            op = self.current_token
            self.next_token()
            node = Node(op, left=node, right=self.unary())
        return node

    def unary(self):
        if self.current_token == "UNARY_MINUS":
            self.next_token()
            return Node("neg", left=self.unary())
        return self.power()

    def power(self):
        node = self.factor()
        if self.current_token == "^":
            self.next_token()
            node = Node("^", left=node, right=self.unary())
        return node

    def factor(self): # numbers, variables, parentheses, and functions, highest precedence
        tok = self.current_token

        if tok == "(":
            self.next_token()
            node = self.expr()
            if self.current_token == ")":
                self.next_token()
            return node

        # I forgot about function handling bruh
        functions = {"sin", "cos", "tan", "log", "ln", "exp", "sqrt"}
        if tok in functions:
            funct_name = tok
            self.next_token() #yummy
            if self.current_token == "(":
                self.next_token() #more yummy
                arg_node = self.expr()
                #print("debug print: function %s with arg %s, current token is %s" % (funct_name, arg_node, self.current_token))
                if self.current_token == ")":
                    self.next_token() #more stuff to eat
                return Node("Funct", left=arg_node, val=funct_name)
            else:
                raise ValueError("Expected '(' after function %s" % funct_name)
        try:
            val = float(tok) if "." in tok else int(tok)#make sure to convert to correct type
            self.next_token()
            return Node("Num", val=float(val))#gah, forgot to turn it into float for evaluation
        except ValueError:
            pass # gotta handle nums and vars later

        self.next_token()
        return Node("Var", val=tok)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tokenize(expr):
    a = list(expr.replace(" ", "")) #remove whitespace
    b = ""
    c = []
    prevType = None
    for i in a:
        if i.isdigit() or i == ".":
            if prevType == "alpha":
                c.append(b)
                b = ""
            b += i
            prevType = "number"
        elif i.isalpha():
            if prevType == "number":
                c.append(b)
                b = ""
            b += i
            prevType = "alpha"
        elif i in "+-*/^": # unary minus needed
            if b:
                c.append(b)
                b = ""
            if i == "-" and (prevType is None or prevType == "operator"  or (c and c[-1] == "(")):
                c.append("UNARY_MINUS")
                prevType = "operator"
                continue
            c.append(i)
            prevType = "operator"
        else:
            prevType = None
            if i == ")":
                prevType = "something"
            if  b:
                c.append(b)
                b = ""
            if not i.isspace():
                c.append(i)
    if b:
        c.append(b)

    functions = {"sin", "cos", "tan", "log", "ln", "exp", "sqrt"}
    tokens = []

    for i, tok in enumerate(c):
        tokens.append(tok)

        if i < len(c) - 1:
            next_tok = c[i + 1]
            numToWord = tok.replace(".", "", 1).isdigit() and next_tok.isalpha()
            numToParens = tok.replace(".", "", 1).isdigit() and next_tok == "("
            parensToNext = tok == ")" and tok not in functions and (isalnum(next_tok) or next_tok == "(")
            varToNext = tok.isalpha() and tok not in functions and (isalnum(next_tok) or next_tok == "(")

            if numToWord or numToParens or parensToNext or varToNext:
                tokens.append("*")

    return tokens
