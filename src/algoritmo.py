from ports import *
import copy
import random

nvar = 4
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


def criar_individuo():
    ind = [0 for _ in range(IND_TAM)]
    cont = nvar - 1

    for i in range(2, nos * 3, 3):
        ind[i - 2] = random.randint(0, cont)
        ind[i - 1] = random.randint(0, cont)
        ind[i] = portas[random.randint(0, len(portas) - 1)]
        cont += 1

    ind[IND_SAIDA] = nos + nvar - 1
    ind[IND_FIT] = -10
    return ind


def criar_tabela():
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
        for j in range(2**i, 2**nvar, 2**(i + 1)):
            tabela[i][j:j + 2**i] = [1 for _ in range(2**i)]

    for i in minTermos:
        tabela[SIM_NL - 2][i] = 1

    return tabela


def simula(ind, tabela):
    t = copy.deepcopy(tabela)
    ativos = ligantes(ind)

    for i in ativos:
        p = ind[(i - nvar + 1) * 3 - 1]
        ent1 = ind[(i - nvar + 1) * 3 - 2]
        ent2 = ind[(i - nvar + 1) * 3 - 3]

        if p == 'OR':
            t[i] = [p_OR(t[ent1][j], t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif p == 'AND':
            t[i] = [p_AND(t[ent1][j], t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif p == 'XOR':
            t[i] = [p_XOR(t[ent1][j], t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)
        elif p == 'NAND':
            t[i] = [p_NAND(t[ent1][j], t[ent2][j]) for j in range(2**nvar)]
            t[i].append(i)

    t[SIM_LSE] = t[ind[IND_SAIDA]]
    t[SIM_LCOMP] = [p_XNOR(t[SIM_LSD][i], t[SIM_LSE][i]) for i in range(2**nvar)]
    t[SIM_LCOMP].append('CP')

    res = [p_XNOR(t[SIM_LSD][i], t[SIM_LSE][i]) for i in range(2**nvar)]
    pontuacao = sum(res)

    return (pontuacao, t)


def ligantes(individuo):
    vlig = [0 for _ in range(nos + nvar)]

    vlig[individuo[IND_SAIDA]] = individuo[IND_SAIDA]

    for i in range(individuo[IND_SAIDA], nvar - 1, -1):
        if vlig[i] != 0:
            vlig[individuo[(i - nvar + 1) * 3 - 2]] = individuo[(i - nvar + 1) * 3 - 2]
            vlig[individuo[(i - nvar + 1) * 3 - 3]] = individuo[(i - nvar + 1) * 3 - 3]

    del vlig[:nvar]
    vlig = [x for x in vlig if x != 0]

    return vlig


def custo(individuo):
    return len(ligantes(individuo))


def mutacao(f, l, tabela):
    filho = f[:]
    ativos = l[:]
    filho[IND_FIT] = -20

    while True:
        gene = random.randint(0, IND_SAIDA - 1)
        nos_mutado = gene // 3 + nvar

        if (gene + 1) % 3 == 0:
            gene_novo = portas[random.randint(0, len(portas) - 1)]
            while gene_novo == filho[gene]:
                gene_novo = portas[random.randint(0, len(portas) - 1)]
            filho[gene] = gene_novo
        else:
            nova_conexao = random.randint(0, nos_mutado - 1)
            while nova_conexao == filho[gene]:
                nova_conexao = random.randint(0, nos_mutado - 1)
            filho[gene] = nova_conexao

        if nos_mutado in ativos:
            break

    filho[IND_FIT] = simula(filho, tabela)[0]
    return filho


def construir_expressao(individuo, no):
    if no < nvar:
        return chr(ord('A') + no)

    base = (no - nvar) * 3
    ent1 = individuo[base]
    ent2 = individuo[base + 1]
    porta = individuo[base + 2]

    e1 = construir_expressao(individuo, ent1)
    e2 = construir_expressao(individuo, ent2)

    if porta == 'AND':
        return f"({e1} . {e2})"
    elif porta == 'OR':
        return f"({e1} + {e2})"
    elif porta == 'XOR':
        return f"({e1} ⊕ {e2})"
    elif porta == 'NAND':
        return f"~({e1} . {e2})"

    return f"({e1} {porta} {e2})"


def executar_algoritmo(callback_progresso=None):

    ind = criar_individuo()
    tabela = criar_tabela()

    pai = ind[:]
    pai[IND_FIT] = simula(pai, tabela)[0]

    melhor = pai[:]
    melhor_perfeito = None

    geracao = 0
    max_geracoes = 50000
    n_filhos = 20

    while geracao < max_geracoes:
        geracao += 1

        if callback_progresso is not None and (geracao % 100 == 0 or geracao == max_geracoes):
            callback_progresso(geracao, max_geracoes)

        ativos = ligantes(pai)

        melhor_filho = None

        for _ in range(n_filhos):
            filho = mutacao(pai, ativos, tabela)

            if melhor_filho is None:
                melhor_filho = filho[:]
                continue

            if melhor_perfeito is None:
                if filho[IND_FIT] > melhor_filho[IND_FIT]:
                    melhor_filho = filho[:]
            else:
                if filho[IND_FIT] == 2**nvar and custo(filho) < custo(melhor_filho):
                    melhor_filho = filho[:]

        if melhor_perfeito is None:
            if melhor_filho[IND_FIT] >= pai[IND_FIT]:
                pai = melhor_filho[:]
        else:
            if melhor_filho[IND_FIT] == 2**nvar and custo(melhor_filho) <= custo(pai):
                pai = melhor_filho[:]

        if pai[IND_FIT] > melhor[IND_FIT]:
            melhor = pai[:]

        if pai[IND_FIT] == 2**nvar:
            if melhor_perfeito is None:
                melhor_perfeito = pai[:]
            elif custo(pai) < custo(melhor_perfeito):
                melhor_perfeito = pai[:]

    if melhor_perfeito is not None:
        individuo_final = melhor_perfeito
        mensagem = "Melhor solução perfeita encontrada."
    else:
        individuo_final = melhor
        mensagem = "Nenhuma solução perfeita encontrada. Melhor indivíduo parcial."

    fitness = individuo_final[IND_FIT]
    nos_ativos = custo(individuo_final)
    expressao = construir_expressao(individuo_final, individuo_final[IND_SAIDA])

    return {
        "mensagem": mensagem,
        "fitness": fitness,
        "geracoes": geracao,
        "nos_ativos": nos_ativos,
        "individuo": individuo_final,
        "expressao": expressao
    }


if __name__ == "__main__":
    resultado = executar_algoritmo()
    print("Gerações:", resultado["geracoes"])
    print(resultado["mensagem"])
    print("Fitness:", resultado["fitness"])
    print("Nós ativos:", resultado["nos_ativos"])
    print("Expressão:", resultado["expressao"])
    print("Indivíduo:", resultado["individuo"])