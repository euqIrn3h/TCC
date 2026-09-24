from ports import *
import copy
import random


PORTAS = ['AND', 'OR', 'XOR', 'NAND']


def calcular_indices(nvar, nos):
    ind_tam = nos * 3 + 2
    ind_saida = nos * 3
    ind_fit = nos * 3 + 1

    sim_nl = nvar + nos + 3
    sim_nc = 2**nvar + 1
    sim_lcomp = sim_nl - 1
    sim_lsd = sim_nl - 2
    sim_lse = sim_nl - 3

    return {
        "IND_TAM": ind_tam,
        "IND_SAIDA": ind_saida,
        "IND_FIT": ind_fit,
        "SIM_NL": sim_nl,
        "SIM_NC": sim_nc,
        "SIM_LCOMP": sim_lcomp,
        "SIM_LSD": sim_lsd,
        "SIM_LSE": sim_lse,
    }


def criar_individuo(nvar, nos, portas, indices):
    ind = [0 for _ in range(indices["IND_TAM"])]
    cont = nvar - 1

    for i in range(2, nos * 3, 3):
        ind[i - 2] = random.randint(0, cont)
        ind[i - 1] = random.randint(0, cont)
        ind[i] = portas[random.randint(0, len(portas) - 1)]
        cont += 1

    ind[indices["IND_SAIDA"]] = random.randint(nvar, nvar + nos - 1)
    ind[indices["IND_FIT"]] = -10
    return ind


def criar_tabela(nvar, nos, mintermos, indices):
    tabela = []

    for _ in range(indices["SIM_NL"]):
        linha = [0 for _ in range(indices["SIM_NC"])]
        tabela.append(linha)

    for i in range(indices["SIM_NL"] - 3):
        tabela[i][indices["SIM_NC"] - 1] = i

    tabela[indices["SIM_LSE"]][indices["SIM_NC"] - 1] = 'SE'
    tabela[indices["SIM_LSD"]][indices["SIM_NC"] - 1] = 'SD'
    tabela[indices["SIM_LCOMP"]][indices["SIM_NC"] - 1] = 'CP'

    for i in range(nvar):
        for j in range(2**i, 2**nvar, 2**(i + 1)):
            tabela[i][j:j + 2**i] = [1 for _ in range(2**i)]

    for i in mintermos:
        if 0 <= i < 2**nvar:
            tabela[indices["SIM_LSD"]][i] = 1

    return tabela


def ligantes(individuo, nvar, nos, indices):
    vlig = [0 for _ in range(nos + nvar)]

    vlig[individuo[indices["IND_SAIDA"]]] = individuo[indices["IND_SAIDA"]]

    for i in range(individuo[indices["IND_SAIDA"]], nvar - 1, -1):
        if vlig[i] != 0:
            vlig[individuo[(i - nvar + 1) * 3 - 2]] = individuo[(i - nvar + 1) * 3 - 2]
            vlig[individuo[(i - nvar + 1) * 3 - 3]] = individuo[(i - nvar + 1) * 3 - 3]

    del vlig[:nvar]
    vlig = [x for x in vlig if x != 0]

    return vlig


def custo(individuo, nvar, nos, indices):
    return len(ligantes(individuo, nvar, nos, indices))


def simula(individuo, tabela, nvar, nos, indices):
    t = copy.deepcopy(tabela)
    ativos = ligantes(individuo, nvar, nos, indices)

    for i in ativos:
        p = individuo[(i - nvar + 1) * 3 - 1]
        ent1 = individuo[(i - nvar + 1) * 3 - 2]
        ent2 = individuo[(i - nvar + 1) * 3 - 3]

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

    t[indices["SIM_LSE"]] = t[individuo[indices["IND_SAIDA"]]]
    t[indices["SIM_LCOMP"]] = [
        p_XNOR(t[indices["SIM_LSD"]][i], t[indices["SIM_LSE"]][i])
        for i in range(2**nvar)
    ]
    t[indices["SIM_LCOMP"]].append('CP')

    res = [
        p_XNOR(t[indices["SIM_LSD"]][i], t[indices["SIM_LSE"]][i])
        for i in range(2**nvar)
    ]
    pontuacao = sum(res)

    return pontuacao, t


def mutacao(filho_base, ativos, tabela, nvar, nos, portas, indices):
    filho = filho_base[:]
    filho[indices["IND_FIT"]] = -20

    while True:
        gene = random.randint(0, indices["IND_SAIDA"])

        # Mutação da saída
        if gene == indices["IND_SAIDA"]:
            nova_saida = random.randint(
                nvar,
                nvar + nos - 1
            )

            while nova_saida == filho[gene]:
                nova_saida = random.randint(
                    nvar,
                    nvar + nos - 1
                )

            filho[gene] = nova_saida
            break

        # Mutação de um nó
        no_mutado = gene // 3 + nvar

        if (gene + 1) % 3 == 0:
            gene_novo = portas[
                random.randint(0, len(portas) - 1)
            ]

            while gene_novo == filho[gene]:
                gene_novo = portas[
                    random.randint(0, len(portas) - 1)
                ]

            filho[gene] = gene_novo

        else:
            nova_conexao = random.randint(
                0,
                no_mutado - 1
            )

            while nova_conexao == filho[gene]:
                nova_conexao = random.randint(
                    0,
                    no_mutado - 1
                )

            filho[gene] = nova_conexao

        if no_mutado in ativos:
            break

    filho[indices["IND_FIT"]] = simula(
        filho,
        tabela,
        nvar,
        nos,
        indices
    )[0]

    return filho


def construir_expressao(individuo, no, nvar):
    if no < nvar:
        return chr(ord('A') + no)

    base = (no - nvar) * 3
    ent1 = individuo[base]
    ent2 = individuo[base + 1]
    porta = individuo[base + 2]

    e1 = construir_expressao(individuo, ent1, nvar)
    e2 = construir_expressao(individuo, ent2, nvar)

    if porta == 'AND':
        return f"({e1} . {e2})"
    elif porta == 'OR':
        return f"({e1} + {e2})"
    elif porta == 'XOR':
        return f"({e1} ⊕ {e2})"
    elif porta == 'NAND':
        return f"~({e1} . {e2})"

    return f"({e1} {porta} {e2})"


def executar_algoritmo(nvar, nos, max_geracoes, n_filhos, mintermos, callback_progresso=None):

    indices = calcular_indices(nvar, nos)
    individuo_inicial = criar_individuo(nvar, nos, PORTAS, indices)
    tabela = criar_tabela(nvar, nos, mintermos, indices)

    pai = individuo_inicial[:]
    pai[indices["IND_FIT"]] = simula(pai, tabela, nvar, nos, indices)[0]

    melhor = pai[:]
    melhor_perfeito = None

    geracao = 0

    while geracao < max_geracoes:
        geracao += 1

        if callback_progresso is not None and (geracao % 100 == 0 or geracao == max_geracoes):
            callback_progresso(geracao, max_geracoes)

        ativos = ligantes(pai, nvar, nos, indices)
        melhor_filho = None

        for _ in range(n_filhos):
            filho = mutacao(pai, ativos, tabela, nvar, nos, PORTAS, indices)

            if melhor_filho is None:
                melhor_filho = filho[:]
                continue

            if melhor_perfeito is None:
                if filho[indices["IND_FIT"]] > melhor_filho[indices["IND_FIT"]]:
                    melhor_filho = filho[:]
            else:
                if (
                    filho[indices["IND_FIT"]] == 2**nvar
                    and custo(filho, nvar, nos, indices) < custo(melhor_filho, nvar, nos, indices)
                ):
                    melhor_filho = filho[:]

        if melhor_perfeito is None:
            if melhor_filho[indices["IND_FIT"]] >= pai[indices["IND_FIT"]]:
                pai = melhor_filho[:]
        else:
            if (
                melhor_filho[indices["IND_FIT"]] == 2**nvar
                and custo(melhor_filho, nvar, nos, indices) <= custo(pai, nvar, nos, indices)
            ):
                pai = melhor_filho[:]

        if pai[indices["IND_FIT"]] > melhor[indices["IND_FIT"]]:
            melhor = pai[:]

        if pai[indices["IND_FIT"]] == 2**nvar:
            if melhor_perfeito is None:
                melhor_perfeito = pai[:]
            elif custo(pai, nvar, nos, indices) < custo(melhor_perfeito, nvar, nos, indices):
                melhor_perfeito = pai[:]

    if melhor_perfeito is not None:
        individuo_final = melhor_perfeito
        mensagem = "Melhor solução perfeita encontrada."
    else:
        individuo_final = melhor
        mensagem = "Nenhuma solução perfeita encontrada. Melhor indivíduo parcial."

    fitness = individuo_final[indices["IND_FIT"]]
    nos_ativos = custo(individuo_final, nvar, nos, indices)
    expressao = construir_expressao(individuo_final, individuo_final[indices["IND_SAIDA"]], nvar)

    return {
        "mensagem": mensagem,
        "fitness": fitness,
        "geracoes": geracao,
        "nos_ativos": nos_ativos,
        "individuo": individuo_final,
        "expressao": expressao
    }


if __name__ == "__main__":
    resultado = executar_algoritmo(
        nvar=3,
        nos=6,
        max_geracoes=50000,
        n_filhos=4,
        mintermos=[0, 1, 3]
    )

    print("Gerações:", resultado["geracoes"])
    print(resultado["mensagem"])
    print("Fitness:", resultado["fitness"])
    print("Nós ativos:", resultado["nos_ativos"])
    print("Expressão:", resultado["expressao"])
    print("Indivíduo:", resultado["individuo"])