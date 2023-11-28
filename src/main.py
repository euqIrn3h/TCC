import random
import copy

random.seed(3)

nvar = 4
portas = ['AND', 'OR', 'XOR', 'NAND']
nos = 10
nFilhos = 4

minTermos = [0, 1, 3, 6, 7, 8, 10, 13]

IND_TAM = nos * 3 * 2
IND_SAIDA = nos * 3
IND_FIT = nos * 3 + 1

SIM_NL = nvar + nos + 3
SIM_NC = 2**nvar + 1
SIM_LCOMP = SIM_NL - 1
SIM_LSD = SIM_NL - 2
SIM_LSE = SIM_NL - 3

ind = []

for i in range(IND_TAM):
    ind.append(0)

cont = nvar - 1

for i in range(2, nos*3, 3):
    ind[i-2] = random.randint(0,cont)
    ind[i-1] = random.randint(0,cont)
    ind[i] = portas[random.randint(0, len(portas)-1)]
    cont = cont + 1

ind[IND_SAIDA] = nos + nvar - 1
ind[IND_FIT] = - 10

tabela = []

for i in range(SIM_NL):
    linha = []
    for j in range(SIM_NC):
        linha.append(0)
    tabela.append(linha)

for i in range(SIM_NL - 3):
    tabela[i][SIM_NC - 1] = i

tabela[SIM_NL - 3][SIM_NC - 1] = 'SE'
tabela[SIM_NL - 2][SIM_NC - 1] = 'SD'
tabela[SIM_NL - 1][SIM_NC - 1] = 'CP'

for i in range(nvar):
    for j in range(2**i, 2**nvar, 2**(i+1)):
        tabela[i][j:j + 2**i] = [1 for k in range(2**i)]

for i in minTermos:
    tabela[SIM_NL -2 ][i] = 1

print(ind)
print(tabela)