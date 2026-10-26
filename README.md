# Micropython CAS Engine

A Computer Algebra System design to run in Micropython with exact fractional arithmetic.

## Features
- **Exact Fraction Engine (`Frac()`): **Support for rational arithmetic, reduction, and decimal/string parsing
- **AST Parser & Simplifier: **Parses expressions with operator precedence, implicit multiplication, and like-term combination in mind
- **Exact Polynomial Solver (`solve_poly()`): **Solves polynomial roots with exact fractions

## Instructions for use
1. make sure you have Python 3.x or a microcontroller flashed with MicroPython ready
2. Clone this repo:
```bash
git clone https://github.com/CrX1x1/CAS.git
cd CAS
```
3. Run the file in REPL:
```bash
python -i solver.py
```
4. Test expressions directly, for example:
```py
>>> Parser(tokenize("-2 * (3x - 4) + 5 - x^2 + sin(x) * 2 + 10 - 4x + 3(x^2 + 1) - 7")).parse()
-2 * (3 * x - 4) + 5 - x^2 + sin(x) * 2 + 10 - 4 * x + 3 * (x^2 + 1) - 7
>>> str(Parser(tokenize("2^(3^2)")).parse())
'2^3^2'
>>> str(Parser(tokenize("(2^3)^2")).parse())
'(2^3)^2'
>>> print(Frac(".75"))
(3/4)
>>> print(simplify(Parser(tokenize("x^2 + x^2")).parse()))
2 * x^2
>>> solve_poly([Frac(1), Frac(-6), Frac(11), Frac(-6)])
[2/1, 3/1, 1/1]
```
