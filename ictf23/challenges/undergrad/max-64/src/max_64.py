import numpy as np
print('When Max goes to the pool and he enters the pool with a stride jump from 64 meters high!! Tell me what your array is and I will tell you his secret: ')
print('**Hint: reshape your array to a 1x27 array**')
x = input()
if x[:2] == '[[':
    x = x[2:]
if x[-2:] == ']]':
    x = x[:-2]
x = x.replace(" ", "")
print("The flag is: ictf{%s}"%x)
