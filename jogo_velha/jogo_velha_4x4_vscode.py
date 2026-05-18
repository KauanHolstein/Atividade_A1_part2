# -*- coding: utf-8 -*-
"""
Jogo da Velha 4x4 com Minimax + Poda Alfa-Beta - Versao VS Code (GUI Tkinter)
==============================================================================
Atividade de Busca Competitiva (Adversarial Search).

Regras:
    - Tabuleiro 4x4 (16 casas).
    - Vence quem alinhar 4 simbolos em linha, coluna ou diagonal.
    - Humano = 'X', IA = 'O'.

Interface: janela grafica usando Tkinter (vem na biblioteca padrao do Python,
nenhuma instalacao adicional necessaria).

Para rodar no VS Code:
    1) Abra a pasta no VS Code.
    2) Abra um terminal (Ctrl + ` ).
    3) Execute:  python jogo_velha_4x4_vscode.py
       (no Windows pode ser:  py jogo_velha_4x4_vscode.py)

Indicadores exibidos a cada jogada da IA:
    - Numero de nos avaliados.
    - Cortes alfa-beta.
    - Tempo de execucao.
    - Melhor jogada escolhida (com seu escore).
"""

import math
import time
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------------------------------------------------------
# CONSTANTES DO JOGO
# ---------------------------------------------------------------------------
JOGADOR_X = 'X'        # humano (minimizador)
JOGADOR_O = 'O'        # IA     (maximizador)
VAZIO     = ' '

TAMANHO      = 4       # tabuleiro 4x4
PROFUNDIDADE = 4       # profundidade maxima do minimax (ajuste: 4 a 6)

VITORIA_O =  10**6
VITORIA_X = -10**6


# ---------------------------------------------------------------------------
# METRICAS DE DESEMPENHO (exigidas pelo enunciado)
# ---------------------------------------------------------------------------
class Metricas:
    def __init__(self):
        self.reset()

    def reset(self):
        self.nos_avaliados = 0
        self.cortes_alfa_beta = 0
        self.tempo = 0.0
        self.melhor_jogada = None
        self.escore_da_melhor_jogada = 0

metricas = Metricas()


# ---------------------------------------------------------------------------
# REPRESENTACAO DO TABULEIRO
# ---------------------------------------------------------------------------
def inicializar_tabuleiro():
    return [[VAZIO] * TAMANHO for _ in range(TAMANHO)]


def obter_movimentos_validos(tabuleiro):
    """Casas vazias, ordenadas pelas centrais primeiro (move ordering)."""
    centro = (TAMANHO - 1) / 2.0
    movs = [(i, j) for i in range(TAMANHO) for j in range(TAMANHO)
            if tabuleiro[i][j] == VAZIO]
    movs.sort(key=lambda m: abs(m[0] - centro) + abs(m[1] - centro))
    return movs


def tabuleiro_cheio(tabuleiro):
    return all(tabuleiro[i][j] != VAZIO
               for i in range(TAMANHO) for j in range(TAMANHO))


# ---------------------------------------------------------------------------
# LINHAS VENCEDORAS - 4 linhas + 4 colunas + 2 diagonais = 10 linhas
# ---------------------------------------------------------------------------
def _gerar_linhas_vencedoras():
    linhas = []
    for i in range(TAMANHO):
        linhas.append([(i, j) for j in range(TAMANHO)])         # horizontais
    for j in range(TAMANHO):
        linhas.append([(i, j) for i in range(TAMANHO)])         # verticais
    linhas.append([(i, i) for i in range(TAMANHO)])             # diagonal
    linhas.append([(i, TAMANHO - 1 - i) for i in range(TAMANHO)])  # anti-diag
    return linhas

LINHAS_VENCEDORAS = _gerar_linhas_vencedoras()


def verificar_vencedor(tabuleiro):
    """Retorna ('X' ou 'O', linha_vencedora) ou (None, None)."""
    for linha in LINHAS_VENCEDORAS:
        vals = [tabuleiro[i][j] for (i, j) in linha]
        if vals[0] != VAZIO and all(v == vals[0] for v in vals):
            return vals[0], linha
    return None, None


# ---------------------------------------------------------------------------
# HEURISTICA DE AVALIACAO
# ---------------------------------------------------------------------------
# Para cada uma das 10 linhas:
#   - se tem AMBOS X e O -> 0 (linha morta)
#   - se so tem O        -> +1, +10, +100 conforme 1, 2 ou 3 simbolos
#   - se so tem X        -> -1, -10, -100 conforme 1, 2 ou 3 simbolos
# Pesos exponenciais fazem a IA priorizar bloquear/criar "3 em linha".
PESOS_O = {0: 0, 1: 1, 2: 10, 3: 100}
PESOS_X = {0: 0, 1: -1, 2: -10, 3: -100}

def avaliar_heuristica(tabuleiro):
    pont = 0
    for linha in LINHAS_VENCEDORAS:
        vals = [tabuleiro[i][j] for (i, j) in linha]
        n_o = vals.count(JOGADOR_O)
        n_x = vals.count(JOGADOR_X)
        if n_o > 0 and n_x > 0:
            continue
        if n_o > 0:
            pont += PESOS_O.get(n_o, 0)
        elif n_x > 0:
            pont += PESOS_X.get(n_x, 0)
    return pont


# ---------------------------------------------------------------------------
# MINIMAX COM PODA ALFA-BETA
# ---------------------------------------------------------------------------
# alfa = melhor valor garantido para MAX (IA) ate aqui.
# beta = melhor valor garantido para MIN (humano) ate aqui.
# Quando alfa >= beta podamos: o adversario acima na arvore nunca deixaria
# o jogo cair nesse ramo. A poda NAO altera a decisao - so reduz o numero
# de nos visitados.
def minimax(tabuleiro, profundidade, alfa, beta, is_maximizando):
    metricas.nos_avaliados += 1

    vencedor, _ = verificar_vencedor(tabuleiro)
    if vencedor == JOGADOR_O:
        return VITORIA_O - (PROFUNDIDADE - profundidade)
    if vencedor == JOGADOR_X:
        return VITORIA_X + (PROFUNDIDADE - profundidade)
    if tabuleiro_cheio(tabuleiro):
        return 0
    if profundidade == 0:
        return avaliar_heuristica(tabuleiro)

    movimentos = obter_movimentos_validos(tabuleiro)

    if is_maximizando:
        melhor = -math.inf
        for (i, j) in movimentos:
            tabuleiro[i][j] = JOGADOR_O
            escore = minimax(tabuleiro, profundidade - 1, alfa, beta, False)
            tabuleiro[i][j] = VAZIO
            if escore > melhor:
                melhor = escore
            if melhor > alfa:
                alfa = melhor
            if alfa >= beta:                              # CORTE BETA
                metricas.cortes_alfa_beta += 1
                break
        return melhor
    else:
        melhor = math.inf
        for (i, j) in movimentos:
            tabuleiro[i][j] = JOGADOR_X
            escore = minimax(tabuleiro, profundidade - 1, alfa, beta, True)
            tabuleiro[i][j] = VAZIO
            if escore < melhor:
                melhor = escore
            if melhor < beta:
                beta = melhor
            if alfa >= beta:                              # CORTE ALFA
                metricas.cortes_alfa_beta += 1
                break
        return melhor


def encontrar_melhor_jogada(tabuleiro):
    """Raiz do minimax: escolhe a jogada com melhor valor para a IA."""
    metricas.reset()
    t0 = time.time()
    melhor_escore = -math.inf
    melhor_jogada = None
    alfa, beta = -math.inf, math.inf

    for (i, j) in obter_movimentos_validos(tabuleiro):
        tabuleiro[i][j] = JOGADOR_O
        escore = minimax(tabuleiro, PROFUNDIDADE - 1, alfa, beta, False)
        tabuleiro[i][j] = VAZIO
        if escore > melhor_escore:
            melhor_escore = escore
            melhor_jogada = (i, j)
        if melhor_escore > alfa:
            alfa = melhor_escore

    metricas.tempo = time.time() - t0
    metricas.melhor_jogada = melhor_jogada
    metricas.escore_da_melhor_jogada = melhor_escore
    return melhor_jogada


# ===========================================================================
# INTERFACE GRAFICA (Tkinter)
# ===========================================================================
COR_FUNDO       = "#1e1e2e"   # fundo da janela (tema escuro)
COR_PAINEL      = "#252535"   # paineis internos
COR_TEXTO       = "#e0e0e0"   # texto claro
COR_BOTAO_BG    = "#2a2a3e"   # fundo dos botoes do tabuleiro
COR_BOTAO_HOVER = "#3a3a55"   # ao passar mouse
COR_X           = "#00bcd4"   # X em ciano
COR_O           = "#ff6b6b"   # O em vermelho claro
COR_VITORIA     = "#4caf50"   # destaque verde para linha vencedora
COR_DESTAQUE    = "#ffd54f"   # amarelo - ultima jogada da IA

FONTE_TITULO    = ("Segoe UI", 18, "bold")
FONTE_STATUS    = ("Segoe UI", 12)
FONTE_BOTAO     = ("Segoe UI", 28, "bold")
FONTE_METRICA   = ("Consolas", 10)


class JogoVelhaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha 4x4 - Minimax + Poda Alfa-Beta")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(False, False)

        self.tabuleiro = inicializar_tabuleiro()
        self.game_over = False
        self.ia_pensando = False
        self.botoes = [[None] * TAMANHO for _ in range(TAMANHO)]

        self._construir_ui()
        self._atualizar_status("Sua vez (X). Clique numa casa para jogar.")

    # ----- construcao da interface -----------------------------------------
    def _construir_ui(self):
        # Titulo
        titulo = tk.Label(
            self.root, text="Jogo da Velha 4x4",
            font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_TEXTO
        )
        titulo.pack(pady=(12, 4))

        subtitulo = tk.Label(
            self.root,
            text=f"Voce (X) vs IA (O)  |  Alinhe 4  |  Profundidade = {PROFUNDIDADE}",
            font=("Segoe UI", 10), bg=COR_FUNDO, fg="#888899"
        )
        subtitulo.pack(pady=(0, 8))

        # Linha de status
        self.status_label = tk.Label(
            self.root, text="", font=FONTE_STATUS,
            bg=COR_FUNDO, fg=COR_TEXTO, width=46
        )
        self.status_label.pack(pady=(0, 8))

        # Tabuleiro 4x4
        frame_tab = tk.Frame(self.root, bg=COR_FUNDO)
        frame_tab.pack(padx=14, pady=4)

        for i in range(TAMANHO):
            for j in range(TAMANHO):
                b = tk.Button(
                    frame_tab, text=" ",
                    font=FONTE_BOTAO,
                    width=3, height=1,
                    bg=COR_BOTAO_BG, fg=COR_TEXTO,
                    activebackground=COR_BOTAO_HOVER,
                    relief="flat", bd=0,
                    command=lambda li=i, co=j: self._jogada_humano(li, co)
                )
                b.grid(row=i, column=j, padx=3, pady=3, ipadx=6, ipady=6)
                self.botoes[i][j] = b

        # Painel de metricas
        frame_met = tk.LabelFrame(
            self.root, text=" Indicadores de desempenho (ultima jogada da IA) ",
            font=("Segoe UI", 9, "bold"),
            bg=COR_PAINEL, fg=COR_TEXTO, bd=1, relief="solid",
            labelanchor="nw"
        )
        frame_met.pack(padx=14, pady=(12, 6), fill="x")

        self.lbl_nos     = tk.Label(frame_met, text="Nos avaliados : -",
                                    font=FONTE_METRICA, bg=COR_PAINEL,
                                    fg=COR_TEXTO, anchor="w")
        self.lbl_cortes  = tk.Label(frame_met, text="Cortes alfa-beta : -",
                                    font=FONTE_METRICA, bg=COR_PAINEL,
                                    fg=COR_TEXTO, anchor="w")
        self.lbl_tempo   = tk.Label(frame_met, text="Tempo de execucao : -",
                                    font=FONTE_METRICA, bg=COR_PAINEL,
                                    fg=COR_TEXTO, anchor="w")
        self.lbl_jogada  = tk.Label(frame_met, text="Melhor jogada : -",
                                    font=FONTE_METRICA, bg=COR_PAINEL,
                                    fg=COR_TEXTO, anchor="w")

        for lbl in (self.lbl_nos, self.lbl_cortes, self.lbl_tempo, self.lbl_jogada):
            lbl.pack(fill="x", padx=8, pady=1)

        # Botoes inferiores
        frame_btn = tk.Frame(self.root, bg=COR_FUNDO)
        frame_btn.pack(pady=(4, 14))

        btn_reset = tk.Button(
            frame_btn, text="Reiniciar Jogo",
            font=("Segoe UI", 10, "bold"),
            bg="#4caf50", fg="white",
            activebackground="#66bb6a", activeforeground="white",
            relief="flat", padx=18, pady=6, bd=0,
            command=self._reiniciar
        )
        btn_reset.pack(side="left", padx=6)

        btn_sair = tk.Button(
            frame_btn, text="Sair",
            font=("Segoe UI", 10, "bold"),
            bg="#5a5a70", fg="white",
            activebackground="#6a6a80", activeforeground="white",
            relief="flat", padx=18, pady=6, bd=0,
            command=self.root.destroy
        )
        btn_sair.pack(side="left", padx=6)

    # ----- helpers de UI ---------------------------------------------------
    def _atualizar_status(self, msg, cor=COR_TEXTO):
        self.status_label.config(text=msg, fg=cor)

    def _atualizar_metricas(self):
        self.lbl_nos.config(text=f"Nos avaliados      : {metricas.nos_avaliados}")
        self.lbl_cortes.config(text=f"Cortes alfa-beta   : {metricas.cortes_alfa_beta}")
        self.lbl_tempo.config(text=f"Tempo de execucao  : {metricas.tempo:.4f} s")
        self.lbl_jogada.config(
            text=f"Melhor jogada      : {metricas.melhor_jogada} "
                 f"(escore = {metricas.escore_da_melhor_jogada})"
        )

    def _pintar_simbolo(self, i, j, simbolo, destaque=False):
        cor = COR_X if simbolo == JOGADOR_X else COR_O
        bg  = COR_DESTAQUE if destaque else COR_BOTAO_BG
        fg  = "#1e1e2e" if destaque else cor
        self.botoes[i][j].config(
            text=simbolo, fg=fg, bg=bg, state="disabled",
            disabledforeground=fg
        )

    def _destacar_vitoria(self, linha):
        for (i, j) in linha:
            self.botoes[i][j].config(bg=COR_VITORIA, disabledforeground="#1e1e2e")

    def _desabilitar_tudo(self):
        for i in range(TAMANHO):
            for j in range(TAMANHO):
                self.botoes[i][j].config(state="disabled")

    # ----- logica do jogo --------------------------------------------------
    def _checar_fim(self):
        vencedor, linha = verificar_vencedor(self.tabuleiro)
        if vencedor:
            self._destacar_vitoria(linha)
            self.game_over = True
            if vencedor == JOGADOR_X:
                self._atualizar_status("Voce venceu! (raro :))", COR_VITORIA)
                messagebox.showinfo("Fim de jogo", "Voce venceu!")
            else:
                self._atualizar_status("A IA venceu!", COR_O)
                messagebox.showinfo("Fim de jogo", "A IA venceu!")
            return True
        if tabuleiro_cheio(self.tabuleiro):
            self.game_over = True
            self._atualizar_status("Empate!", COR_DESTAQUE)
            messagebox.showinfo("Fim de jogo", "Empate!")
            return True
        return False

    def _jogada_humano(self, linha, coluna):
        if self.game_over or self.ia_pensando:
            return
        if self.tabuleiro[linha][coluna] != VAZIO:
            return

        self.tabuleiro[linha][coluna] = JOGADOR_X
        self._pintar_simbolo(linha, coluna, JOGADOR_X)

        if self._checar_fim():
            return

        self._atualizar_status("IA (O) pensando...", COR_DESTAQUE)
        self.ia_pensando = True
        # roda a IA depois de um pequeno delay para a UI atualizar a mensagem
        self.root.after(100, self._jogada_ia)

    def _jogada_ia(self):
        jogada = encontrar_melhor_jogada(self.tabuleiro)
        self.ia_pensando = False

        if jogada is None:
            self._checar_fim()
            return

        i, j = jogada
        self.tabuleiro[i][j] = JOGADOR_O
        self._pintar_simbolo(i, j, JOGADOR_O, destaque=True)
        self._atualizar_metricas()

        if not self._checar_fim():
            self._atualizar_status("Sua vez (X).", COR_TEXTO)

    def _reiniciar(self):
        self.tabuleiro = inicializar_tabuleiro()
        self.game_over = False
        self.ia_pensando = False
        for i in range(TAMANHO):
            for j in range(TAMANHO):
                self.botoes[i][j].config(
                    text=" ", state="normal",
                    bg=COR_BOTAO_BG, fg=COR_TEXTO
                )
        self.lbl_nos.config(text="Nos avaliados      : -")
        self.lbl_cortes.config(text="Cortes alfa-beta   : -")
        self.lbl_tempo.config(text="Tempo de execucao  : -")
        self.lbl_jogada.config(text="Melhor jogada      : -")
        self._atualizar_status("Novo jogo! Sua vez (X).")


# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    try:
        # tema mais elegante quando disponivel
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    JogoVelhaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
