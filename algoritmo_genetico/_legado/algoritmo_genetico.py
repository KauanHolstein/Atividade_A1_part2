"""
Simulação Didática de Algoritmo Genético
-----------------------------------------
Objetivo: encontrar uma sequência-alvo formada por 10 inteiros distintos
no intervalo [1, 20], em ordem crescente.

Cada indivíduo é uma lista de 10 inteiros distintos em [1, 20], sempre
em ordem crescente. A função de aptidão conta quantos números do
indivíduo também aparecem na sequência-alvo (posição irrelevante).

Execução: python algoritmo_genetico.py
"""

import random
import sys

# Garante UTF-8 no console (corrige acentos quebrados no Windows/PowerShell).
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =====================================================================
# FUNÇÕES DE REPRESENTAÇÃO
# =====================================================================

def gerar_individuo():
    """Gera um indivíduo: 10 inteiros distintos em [1, 20], ordem crescente."""
    individuo = random.sample(range(1, 21), 10)
    individuo.sort()
    return individuo


def gerar_populacao(tamanho=20):
    """Gera uma população aleatória com `tamanho` indivíduos."""
    return [gerar_individuo() for _ in range(tamanho)]


def validar_individuo(individuo):
    """Garante que um indivíduo respeita as regras (10 distintos, [1,20], crescente)."""
    assert len(individuo) == 10, "Indivíduo deve ter 10 números."
    assert len(set(individuo)) == 10, "Os 10 números devem ser distintos."
    assert all(1 <= n <= 20 for n in individuo), "Todos os números devem estar em [1, 20]."
    assert individuo == sorted(individuo), "O indivíduo deve estar em ordem crescente."


# =====================================================================
# FUNÇÃO DE APTIDÃO
# =====================================================================

def calcular_aptidao(individuo, alvo):
    """Conta quantos números do indivíduo também aparecem na sequência-alvo."""
    return len(set(individuo) & set(alvo))


# =====================================================================
# OPERADORES GENÉTICOS
# =====================================================================

def torneio(populacao, aptidoes, k=2):
    """
    Seleção por torneio de tamanho k.
    Sorteia k indivíduos da população; o de maior aptidão vence.
    Retorna (indice_vencedor, indices_concorrentes).
    """
    concorrentes = random.sample(range(len(populacao)), k)
    vencedor = max(concorrentes, key=lambda i: aptidoes[i])
    return vencedor, concorrentes


def cruzamento(pai1, pai2):
    """
    Cruzamento de 1 ponto de corte na 5ª posição.
    filho_bruto = primeiros 5 do Pai 1 + últimos 5 do Pai 2.
    Trata duplicatas substituindo por números aleatórios de [1, 20]
    que ainda não estejam no filho. Retorna o filho em ordem crescente.
    """
    parte1 = pai1[:5]
    parte2 = pai2[5:]
    filho_bruto = parte1 + parte2

    # Tratamento de duplicatas: preservar a primeira ocorrência e
    # substituir as repetidas por números ainda não presentes.
    filho_corrigido = []
    vistos = set()
    posicoes_repetidas = []

    for i, num in enumerate(filho_bruto):
        if num not in vistos:
            filho_corrigido.append(num)
            vistos.add(num)
        else:
            filho_corrigido.append(None)  # marcador temporário
            posicoes_repetidas.append(i)

    # Preenche posições repetidas com números aleatórios ainda não usados
    for pos in posicoes_repetidas:
        disponiveis = [n for n in range(1, 21) if n not in vistos]
        novo = random.choice(disponiveis)
        filho_corrigido[pos] = novo
        vistos.add(novo)

    filho_corrigido.sort()
    return filho_bruto, filho_corrigido


def mutacao(individuo):
    """
    Mutação: escolhe 1 posição aleatória e substitui o número
    por outro de [1, 20] que ainda não esteja na lista.
    Retorna o indivíduo mutado em ordem crescente.
    """
    mutado = individuo.copy()
    pos = random.randrange(len(mutado))
    valor_antigo = mutado[pos]

    disponiveis = [n for n in range(1, 21) if n not in mutado]
    if not disponiveis:
        # Caso (improvável) em que todos os 20 números já estão presentes.
        return sorted(mutado), pos, valor_antigo, valor_antigo

    novo = random.choice(disponiveis)
    mutado[pos] = novo
    mutado.sort()
    return mutado, pos, valor_antigo, novo


def atualizar_populacao(populacao, aptidoes, filho, aptidao_filho):
    """
    Atualização com elitismo:
    - O melhor indivíduo da geração atual é sempre preservado.
    - Se a aptidão do filho for MAIOR que a do pior indivíduo,
      o filho substitui o pior. Caso contrário, é descartado.
    Retorna (acao, indice_substituido_ou_None).
    """
    indice_pior = min(range(len(populacao)), key=lambda i: aptidoes[i])
    aptidao_pior = aptidoes[indice_pior]

    if aptidao_filho > aptidao_pior:
        populacao[indice_pior] = filho
        aptidoes[indice_pior] = aptidao_filho
        return f"Filho substituiu o indivíduo {indice_pior} (aptidão {aptidao_pior} -> {aptidao_filho})", indice_pior
    else:
        return f"Filho descartado (aptidão {aptidao_filho} <= pior aptidão {aptidao_pior})", None


# =====================================================================
# IMPRESSÃO AUXILIAR
# =====================================================================

def imprimir_populacao(populacao, aptidoes):
    """Exibe tabela: índice, lista, aptidão."""
    print(f"  {'Idx':>3} | {'Indivíduo':<45} | Aptidão")
    print(f"  {'-'*3}-+-{'-'*45}-+--------")
    for i, (ind, apt) in enumerate(zip(populacao, aptidoes)):
        print(f"  {i:>3} | {str(ind):<45} | {apt:>5}")


# =====================================================================
# LOOP PRINCIPAL DO AG
# =====================================================================

def executar_ag(alvo,
                populacao_inicial=None,
                max_geracoes=100,
                limiar_estagnacao=20,
                seed=None):
    """
    Executa o Algoritmo Genético.

    Parâmetros:
    - alvo: lista de 10 inteiros distintos em [1, 20], em ordem crescente (secreta).
    - populacao_inicial: lista de 20 indivíduos ou None para gerar aleatoriamente.
    - max_geracoes: número máximo de gerações.
    - limiar_estagnacao: número de gerações consecutivas sem melhora para parar.
    - seed: semente opcional para reprodutibilidade.

    Retorna dicionário com: melhor_individuo, melhor_aptidao,
    geracoes_executadas, motivo_parada.
    """
    if seed is not None:
        random.seed(seed)

    # --- População inicial -------------------------------------------------
    if populacao_inicial is None:
        populacao = gerar_populacao(20)
    else:
        assert len(populacao_inicial) == 20, "A população inicial deve ter 20 indivíduos."
        populacao = [sorted(ind) for ind in populacao_inicial]

    for ind in populacao:
        validar_individuo(ind)

    aptidoes = [calcular_aptidao(ind, alvo) for ind in populacao]

    melhor_aptidao_global = max(aptidoes)
    geracoes_sem_melhora = 0
    motivo_parada = "Limite máximo de gerações atingido"
    geracao_final = 0

    # --- Verificação inicial (antes de qualquer iteração) -----------------
    if melhor_aptidao_global == 10:
        idx_melhor = aptidoes.index(10)
        print("\n>>> Solução encontrada já na população inicial! <<<")
        return {
            "melhor_individuo": populacao[idx_melhor],
            "melhor_aptidao": 10,
            "geracoes_executadas": 0,
            "motivo_parada": "Aptidão máxima (10) atingida na população inicial",
        }

    # --- Iteração principal ------------------------------------------------
    for geracao in range(1, max_geracoes + 1):
        geracao_final = geracao
        print("\n" + "=" * 72)
        print(f"GERAÇÃO {geracao}")
        print("=" * 72)

        # 1) AVALIAÇÃO
        print("\n[1] AVALIAÇÃO DA POPULAÇÃO")
        imprimir_populacao(populacao, aptidoes)

        # 2) SELEÇÃO POR TORNEIO (dois torneios independentes, k=2)
        idx_pai1, conc1 = torneio(populacao, aptidoes, k=2)
        idx_pai2, conc2 = torneio(populacao, aptidoes, k=2)
        pai1 = populacao[idx_pai1]
        pai2 = populacao[idx_pai2]

        print("\n[2] SELEÇÃO POR TORNEIO (k=2)")
        print(f"  Torneio 1 -> concorrentes: índices {conc1} "
              f"(aptidões {[aptidoes[i] for i in conc1]})")
        print(f"             vencedor: índice {idx_pai1} | Pai 1 = {pai1} "
              f"(aptidão {aptidoes[idx_pai1]})")
        print(f"  Torneio 2 -> concorrentes: índices {conc2} "
              f"(aptidões {[aptidoes[i] for i in conc2]})")
        print(f"             vencedor: índice {idx_pai2} | Pai 2 = {pai2} "
              f"(aptidão {aptidoes[idx_pai2]})")

        # 3) CRUZAMENTO
        filho_bruto, filho_apos_cruz = cruzamento(pai1, pai2)
        print("\n[3] CRUZAMENTO (corte na 5ª posição)")
        print(f"  Pai 1 (5 primeiros)  = {pai1[:5]}")
        print(f"  Pai 2 (5 últimos)    = {pai2[5:]}")
        print(f"  Filho bruto          = {filho_bruto}")
        print(f"  Filho após correção  = {filho_apos_cruz} (duplicatas tratadas e ordenado)")

        # 4) MUTAÇÃO
        filho_mutado, pos_mut, val_antigo, val_novo = mutacao(filho_apos_cruz)
        validar_individuo(filho_mutado)
        print("\n[4] MUTAÇÃO")
        print(f"  Posição sorteada     = {pos_mut}")
        print(f"  Substituição         = {val_antigo} -> {val_novo}")
        print(f"  Filho após mutação   = {filho_mutado}")

        # 5) AVALIAÇÃO DO FILHO
        aptidao_filho = calcular_aptidao(filho_mutado, alvo)
        print("\n[5] AVALIAÇÃO DO FILHO")
        print(f"  Aptidão do filho     = {aptidao_filho}")

        # 6) ATUALIZAÇÃO COM ELITISMO
        # Como o filho só substitui o PIOR e somente quando é ESTRITAMENTE
        # melhor, a aptidão máxima da população nunca diminui — ou seja,
        # o melhor indivíduo é naturalmente preservado a cada geração.
        acao, _ = atualizar_populacao(populacao, aptidoes,
                                      filho_mutado, aptidao_filho)

        print("\n[6] ATUALIZAÇÃO COM ELITISMO")
        print(f"  {acao}")

        # Estatísticas da geração
        melhor_geracao = max(aptidoes)
        idx_melhor_geracao = aptidoes.index(melhor_geracao)
        print(f"\n  Melhor da geração: índice {idx_melhor_geracao} = "
              f"{populacao[idx_melhor_geracao]} | aptidão = {melhor_geracao}")

        # Atualiza controle de estagnação
        if melhor_geracao > melhor_aptidao_global:
            melhor_aptidao_global = melhor_geracao
            geracoes_sem_melhora = 0
        else:
            geracoes_sem_melhora += 1

        # CRITÉRIOS DE PARADA -------------------------------------------
        if melhor_geracao == 10:
            motivo_parada = "Aptidão máxima (10) atingida"
            print(f"\n*** Critério de parada: {motivo_parada} ***")
            break

        if geracoes_sem_melhora >= limiar_estagnacao:
            motivo_parada = (f"Estagnação: {limiar_estagnacao} gerações "
                             f"consecutivas sem melhora")
            print(f"\n*** Critério de parada: {motivo_parada} ***")
            break
    else:
        motivo_parada = f"Limite de {max_geracoes} gerações atingido"

    # --- Resultado final ---------------------------------------------------
    idx_final = max(range(len(populacao)), key=lambda i: aptidoes[i])
    melhor_individuo = populacao[idx_final]
    melhor_aptidao = aptidoes[idx_final]

    print("\n" + "#" * 72)
    print("RESULTADO FINAL")
    print("#" * 72)
    print(f"Sequência-alvo (revelada):  {alvo}")
    print(f"Melhor indivíduo encontrado: {melhor_individuo}")
    print(f"Aptidão final:               {melhor_aptidao} / 10")
    print(f"Gerações executadas:         {geracao_final}")
    print(f"Motivo da parada:            {motivo_parada}")

    return {
        "melhor_individuo": melhor_individuo,
        "melhor_aptidao": melhor_aptidao,
        "geracoes_executadas": geracao_final,
        "motivo_parada": motivo_parada,
    }


# =====================================================================
# INTERFACE COM O USUÁRIO
# =====================================================================

def ler_lista_inteiros(prompt):
    """Lê uma lista de 10 inteiros distintos em [1, 20] do usuário."""
    while True:
        texto = input(prompt).strip()
        try:
            numeros = [int(x) for x in texto.replace(",", " ").split()]
        except ValueError:
            print("  Entrada inválida. Use apenas números separados por espaço ou vírgula.")
            continue
        if len(numeros) != 10:
            print("  É necessário informar exatamente 10 números.")
            continue
        if len(set(numeros)) != 10:
            print("  Os 10 números devem ser distintos.")
            continue
        if not all(1 <= n <= 20 for n in numeros):
            print("  Todos os números devem estar entre 1 e 20.")
            continue
        return sorted(numeros)


def configurar_e_executar():
    """Função interativa de configuração do AG."""
    print("=" * 72)
    print("  SIMULAÇÃO DIDÁTICA DE ALGORITMO GENÉTICO")
    print("=" * 72)

    # --- Sequência-alvo ----------------------------------------------------
    print("\nComo deseja definir a sequência-alvo?")
    print("  [1] Informar manualmente")
    print("  [2] Gerar aleatoriamente")
    op = input("Opção (1/2) [padrão 2]: ").strip() or "2"

    if op == "1":
        alvo = ler_lista_inteiros("  Informe 10 números distintos em [1,20]: ")
    else:
        alvo = gerar_individuo()
        print("  (Sequência-alvo gerada aleatoriamente e mantida secreta)")

    # --- População inicial -------------------------------------------------
    print("\nComo deseja gerar a população inicial?")
    print("  [1] Gerar 20 indivíduos aleatoriamente")
    print("  [2] Informar manualmente os 20 indivíduos")
    op = input("Opção (1/2) [padrão 1]: ").strip() or "1"

    populacao_inicial = None
    if op == "2":
        populacao_inicial = []
        for i in range(20):
            ind = ler_lista_inteiros(f"  Indivíduo {i+1}/20: ")
            populacao_inicial.append(ind)

    # --- Parâmetros --------------------------------------------------------
    txt = input("\nNúmero máximo de gerações [padrão 100]: ").strip()
    max_ger = int(txt) if txt else 100

    txt = input("Limiar de estagnação (gerações sem melhora) [padrão 20]: ").strip()
    limiar = int(txt) if txt else 20

    txt = input("Semente aleatória (opcional, ENTER para nenhuma): ").strip()
    seed = int(txt) if txt else None

    return executar_ag(alvo,
                       populacao_inicial=populacao_inicial,
                       max_geracoes=max_ger,
                       limiar_estagnacao=limiar,
                       seed=seed)


# =====================================================================
# EXEMPLO DE EXECUÇÃO
# =====================================================================

if __name__ == "__main__":
    # Ao dar "Run" neste arquivo, abre direto a interface gráfica.
    # Se a interface não estiver disponível (sem tkinter), cai no exemplo CLI.
    try:
        import tkinter as tk
        from tkinter import ttk
        import interface_ag
        root = tk.Tk()
        try:
            style = ttk.Style()
            if "vista" in style.theme_names():
                style.theme_use("vista")
        except Exception:
            pass
        interface_ag.InterfaceAG(root)
        root.mainloop()
    except Exception as erro:
        print(f"[Interface gráfica indisponível: {erro}]")
        print("Executando exemplo automático no terminal...\n")
        executar_ag(
            alvo=gerar_individuo(),
            populacao_inicial=None,
            max_geracoes=100,
            limiar_estagnacao=20,
            seed=42,
        )
