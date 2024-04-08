from CONST_VARS import *
from ports import *
import copy
import random

def simula(ind, tabela):
    t = copy.deepcopy(tabela)
    ativos = ligantes(ind)

    for i in ativos:
        p = ind[(i-nvar+1)*3 - 1]
        ent1 = ind[(i-nvar+1)*3 - 2]        
        ent2 = ind[(i-nvar+1)*3 - 3]

        if(p == 'OR'):
            t[i] = [p_OR(t[ent1][j],t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif(p == 'AND'):
            t[i] = [p_AND(t[ent1][j],t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif(p == 'XOR'):
            t[i] = [p_XOR(t[ent1][j],t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif(p == 'NAND'):
            t[i] = [p_NAND(t[ent1][j],t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)

    t[SIM_LSE] = t[ind[IND_SAIDA]]
    t[SIM_LCOMP] = [p_XNOR(t[SIM_LSD][i],t[SIM_LSE][i]) for i in range(2**nvar)]
    t[SIM_LCOMP].append('CP')

    res = [p_XNOR(t[SIM_LSD][i],t[SIM_LSE][i]) for i in range(2**nvar)]
    pontuacao = 0

    for i in range(2**nvar):
        pontuacao = pontuacao + res[i]
    
    return (pontuacao,t)

def ligantes(individuo):
    vlig = []
    for i in range(nos + nvar):
        vlig.append(0)
    
    vlig[ind[IND_SAIDA]] = ind[IND_SAIDA]

    for i in range(ind[IND_SAIDA], nvar-1, -1):
        if(vlig[i] != 0):
            vlig[individuo[(i-nvar+1)*3 - 2]] = individuo[(i-nvar+1)*3 - 2]
            vlig[individuo[(i-nvar+1)*3 - 3]] = individuo[(i-nvar+1)*3 - 3]
    
    del vlig[:nvar]

    while 0 in vlig:
        vlig.remove(0)
    
    return vlig

def mutacao(f, l, tabela):
 
    filho = f[:]
    ativos = l[:]
    genes_sorteados = []
    nos_mutados = []
    filho[IND_FIT] = -20

    while True:
        gene = random.randint(0, IND_SAIDA - 1)
        nos_mutado = gene//3 + nvar
        genes_sorteados.append(gene)
        nos_mutados.append(nos_mutado)

        if((gene + 1) % 3 == 0):
            gene_novo = portas[random.randint(0, len(portas)-1)]
            while(gene_novo == filho[gene]):
                gene_novo = portas[random.randint(0, len(portas)-1)]
            filho[gene] = gene_novo
        else:
            nova_conexao = random.randint(0, nos_mutado-1)
            while(nova_conexao == filho[gene]):
                nova_conexao = random.randint(0, nos_mutado-1)
            filho[gene] = nova_conexao

        if(nos_mutado in ativos):
            break
    
    filho[IND_FIT] = simula(filho, tabela)[0]
    return filho