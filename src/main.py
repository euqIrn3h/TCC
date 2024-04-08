from CONST_VARS import *
import random
from evo import *

def main():
    pai = ind[:]
    pai[IND_FIT] = simula(pai, tabela)[0]

    geracao = 0
    while(pai[IND_FIT] < 2**nvar):
        geracao = geracao + 1
        
        ativos = ligantes(pai)
        filho = mutacao(pai, ativos, tabela)

        if(filho[IND_FIT] >= pai[IND_FIT]):
            pai = filho[:]

    print(pai)

random.seed(3)

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


main()