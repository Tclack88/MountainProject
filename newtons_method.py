import numpy as np
#from sympy import Symbol, diff, lambdify

def deriv(func,x):
    # approximate a derivative with the limit definition
    h = 1e-5 # "an infintesimal"
    return (func(x+h) - func(x))/h

def next_x(func, x):
    d_func = deriv(func, x)
    return x - func(x)/d_func

def func(x):
    return x**3 - 2*x - 2
def func2(x):
    return x**5 + x**4 - 5
def func3(x):
    return x**3 + x - 1
def func4(x):
    return x**5 - 3*x + 3


x = 1

for i in range(10):
    x = next_x(func,x)
    print(f"iteration {i+1}:\t{x}")

x = 1
print()
for i in range(10):
    x = next_x(func2,x)
    print(f"iteration {i+1}:\t{x}")

x = 1
print()
for i in range(10):
    x = next_x(func3,x)
    print(f"iteration {i+1}:\t{x}")

x = -2
print()
for i in range(10):
    x = next_x(func4,x)
    print(f"iteration {i+1}:\t{x}")
