nvar = 3
portas = ['AND', 'OR', 'XOR', 'NAND']
nos = 6
nFilhos = 4

minTermos = [0, 1, 3]

IND_TAM = nos * 3 + 2
IND_SAIDA = nos * 3
IND_FIT = nos * 3 + 1

SIM_NL = nvar + nos + 3
SIM_NC = 2**nvar + 1
SIM_LCOMP = SIM_NL - 1
SIM_LSD = SIM_NL - 2
SIM_LSE = SIM_NL - 3

ind = []