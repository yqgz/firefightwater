from math import *

# 数值转换为大写字母串
def num2Capital(j):
    cell = ''
    while j>=0:
        cell = chr(j%26 + 65)+cell
        j = floor(j / 26) - 1
    return cell

# 数值转换为大写字母串
def capital2Num(str):
    ret = 0
    if str != '':
        str.upper()
        l = list(str)
        ret += ord(l[0])-65
        l.pop(0)
        for a in l:
            ret = (ret + 1) * 26
            ret += (ord(a) - 65)

    return ret