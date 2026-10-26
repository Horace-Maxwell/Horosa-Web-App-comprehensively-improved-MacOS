import random
from gua_dict import *

def qigua():
    stalks_first = 30 
    dividers = sorted(random.sample(range(10, stalks_first), 1))
    division_first  = [a - b for a, b in zip(dividers + [stalks_first+10], [10] + dividers)]
    division_second = division_first[1] -  sorted(random.sample(range(1,17), 1))[0]
    division_third = division_first[1] - division_second
    top = division_first[0] % 4 
    if top == 0:
        top = 4
    middle = division_second % 4 
    if middle == 0:
        middle = 4
    bottom = division_third % 4 
    if bottom  == 0:
        bottom = 4
    gua = str(top) + str(middle) + str(bottom)
    return gua_dict.get(gua)

