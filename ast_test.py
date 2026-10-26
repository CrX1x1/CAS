class Frac:
    """Small exact rational type used by the parser."""
    __slots__ = ("numerator", "denominator")

    def __init__(self, numerator=0, denominator=1):
        if isinstance(numerator, Frac) and isinstance(denominator, Frac): #used AI for patching this btw
            numerator, denominator = (
                numerator.numerator * denominator.denominator,
                numerator.denominator * denominator.numerator
            )
        # Handle Frac alone (copy)
        elif isinstance(numerator, Frac):
            numerator, denominator = numerator.numerator, numerator.denominator
        elif isinstance(numerator, str):
            text = numerator.strip()
            if "/" in text:
                numerator, denominator = (int(part) for part in text.split("/", 1))
            elif "." in text:
                whole, fraction = text.split(".", 1)
                sign = -1 if whole.startswith("-") else 1
                whole = whole.lstrip("+-") or "0"
                numerator = sign * (int(whole) * 10 ** len(fraction) + int(fraction or 0))
                denominator = 10 ** len(fraction)
            else:
                numerator = int(text)
        elif isinstance(numerator, float):
            return self.__init__(str(numerator), denominator)

        numerator, denominator = int(numerator), int(denominator)
        if denominator == 0:
            raise ZeroDivisionError("fraction denominator is zero")
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        divisor = self._gcd(abs(numerator), denominator)
        self.numerator = numerator // divisor
        self.denominator = denominator // divisor

    @staticmethod
    def _gcd(a, b):
        while b:
            a, b = b, a % b
        return a or 1

    def _coerce(self, other):
        return other if isinstance(other, Frac) else Frac(other)

    def __add__(self, other):
        other = self._coerce(other)
        return Frac(self.numerator * other.denominator + other.numerator * self.denominator,
                self.denominator * other.denominator)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __mul__(self, other):
        other = self._coerce(other)
        return Frac(self.numerator * other.numerator, self.denominator * other.denominator)

    def __truediv__(self, other):
        other = self._coerce(other)
        return Frac(self.numerator * other.denominator, self.denominator * other.numerator)

    def __neg__(self):
        return Frac(-self.numerator, self.denominator)

    def __pow__(self, exponent):
        if isinstance(exponent, Frac):
            if exponent.denominator != 1:
                raise ValueError("Go bother me about fractional exponents later or submit a PR lol")
            exponent = exponent.numerator
        if exponent < 0:
            return Frac(self.denominator ** -exponent, self.numerator ** -exponent)
        return Frac(self.numerator ** exponent, self.denominator ** exponent)

    def __ge__(self, other):
        other = self._coerce(other)
        return self.numerator * other.denominator >= other.numerator * self.denominator
    def __eq__(self, other):
        other = self._coerce(other)
        return self.numerator * other.denominator == other.numerator * self.denominator
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        other = self._coerce(other)
        return self.numerator * other.denominator < other.numerator * self.denominator
    def __bool__(self):
        return self.numerator != 0
    def __float__(self):
        return self.numerator / self.denominator
    def __int__(self):
        return self.numerator // self.denominator
    def __repr__(self):
        return "Frac(%d, %d)" % (self.numerator, self.denominator)
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        return "(%d/%d)" % (self.numerator, self.denominator)
    def __hash__(self):
        return hash((self.numerator, self.denominator))
    def __repr__(self):
        return "%d/%d" % (self.numerator, self.denominator)
    


class Node:
    __slots__ = ("op", "left", "right", "val")
    def __init__(self, op, left=None, right=None, val=None):
        self.op = op
        self.left = left
        self.right = right
        self.val = val
    def __repr__(self):
        return str(self)
    def __str__(self):
        precedence = {
            "Num": 4,
            "Var": 4,
            "neg": 3,
            "^": 2,
            "*": 1,
            "/": 1,
            "+": 0,
            "-": 0
        }
        if self.op in ("Num", "Var"):
            return str(self.val)
        if self.op == "neg":
            return "-%s" % str(self.left)
        if self.op == "Funct":
            return "%s(%s)" % (self.val, str(self.left))
        if self.op == "^": #exponents get special attention smh
            left_str = str(self.left)
            right_str = str(self.right)

            if self.left and self.left.op == "^":
                left_str = "(%s)" % left_str
            elif self.left and self.left.op in precedence and precedence[self.left.op] < precedence[self.op]:
                left_str = "(%s)" % left_str
            if self.right and self.right.op in precedence and precedence[self.right.op] < precedence[self.op]:
                right_str = "(%s)" % right_str
            return "%s^%s" % (left_str, right_str)
        if self.op in precedence:
            left_str = str(self.left)
            right_str = str(self.right)
            if self.left and self.left.op in precedence and precedence[self.left.op] < precedence[self.op]:
                left_str = "(%s)" % left_str
            if self.right and self.right.op in precedence and precedence[self.right.op] < precedence[self.op]:
                right_str = "(%s)" % right_str
            return "%s %s %s" % (left_str, self.op, right_str)
        return "(%s %s %s)" % (str(self.left), self.op, str(self.right))
def add(l, r): return Node("+", l, r)
def sub(l, r): return Node("-", l, r)
def mul(l, r): return Node("*", l, r)
def div(l, r): return Node("/", l, r)
def pow(l, r): return Node("^", l, r)
def Var(name): return Node("Var", val=name)
def Num(n): return Node("Num", val=n)


def fraction_value(value):
    """Convert parser number values to Frac without introducing float error."""
    if isinstance(value, Frac):
        return value
    if isinstance(value, float):
        return Frac(str(value))
    return Frac(value)


def numeric_fraction(node):
    """Return an exact value for a numeric expression, or None otherwise."""
    if isinstance(node, Frac):
        return Frac(node.numerator, node.denominator)
    if not isinstance(node, Node):
        return None
    if node.op == "Num":
        return fraction_value(node.val)
    if node.op == "neg":
        value = numeric_fraction(node.left)
        return -value if value is not None else None
    if node.op in ("+", "-", "*", "/", "^"):
        left = numeric_fraction(node.left)
        right = numeric_fraction(node.right)
        if left is None or right is None:
            return None
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            return left / right
        if right.denominator == 1 and right >= 0:
            return left ** right.numerator
    return None

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
            right = self.unary()
            if op == "/":
                left_value = numeric_fraction(node)
                right_value = numeric_fraction(right)
                if left_value is not None and right_value is not None:
                    node = Node("Num", val=Frac(left_value, right_value))
                    continue
            node = Node(op, left=node, right=right)
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
            return Node("Num", val=Frac(val, 1))#gah, forgot to turn it into float for evaluation
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
