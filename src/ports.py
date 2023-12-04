def p_OR(x,y):
    return 1 if x == 1 else y

def p_AND(x,y):
    return 0 if x == 0 else y

def p_XOR(x,y):
    return 1 if x != y else 0

def p_XNOR(x,y):
    return 1 if x == y else 0

def p_NAND(x,y):
    return 0 if x == y == 1 else 1