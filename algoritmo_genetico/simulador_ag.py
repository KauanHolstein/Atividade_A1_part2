"""
Simulador de Algoritmo Genético — arquivo único.
=================================================
Abra este arquivo no VS Code e clique em Run (ou F5).
A interface gráfica abre automaticamente.

Sem dependências externas — usa apenas a biblioteca padrão (random, tkinter).
"""

import io
import queue
import random
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Garante UTF-8 no console do Windows (acentos em PT-BR).
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =====================================================================
# REPRESENTAÇÃO
# =====================================================================

def gerar_individuo():
    """Gera um indivíduo: 10 inteiros distintos em [1, 20], ordem crescente."""
    individuo = random.sample(range(1, 21), 10)
    individuo.sort()
    return individuo


def gerar_populacao(tamanho=20):
    """Gera uma população aleatória."""
    return [gerar_individuo() for _ in range(tamanho)]


def validar_individuo(individuo):
    """Garante 10 distintos em [1,20] em ordem crescente."""
    assert len(individuo) == 10
    assert len(set(individuo)) == 10
    assert all(1 <= n <= 20 for n in individuo)
    assert individuo == sorted(individuo)


# =====================================================================
# APTIDÃO
# =====================================================================

def calcular_aptidao(individuo, alvo):
    """Quantos números do indivíduo aparecem na sequência-alvo."""
    return len(set(individuo) & set(alvo))


# =====================================================================
# OPERADORES GENÉTICOS
# =====================================================================

def torneio(populacao, aptidoes, k=2):
    """Torneio de tamanho k. Retorna (índice vencedor, índices concorrentes)."""
    concorrentes = random.sample(range(len(populacao)), k)
    vencedor = max(concorrentes, key=lambda i: aptidoes[i])
    return vencedor, concorrentes


def cruzamento(pai1, pai2):
    """Cruzamento de 1 ponto na 5ª posição, com tratamento de duplicatas."""
    filho_bruto = pai1[:5] + pai2[5:]

    filho_corrigido = []
    vistos = set()
    posicoes_repetidas = []

    for i, num in enumerate(filho_bruto):
        if num not in vistos:
            filho_corrigido.append(num)
            vistos.add(num)
        else:
            filho_corrigido.append(None)
            posicoes_repetidas.append(i)

    for pos in posicoes_repetidas:
        disponiveis = [n for n in range(1, 21) if n not in vistos]
        novo = random.choice(disponiveis)
        filho_corrigido[pos] = novo
        vistos.add(novo)

    filho_corrigido.sort()
    return filho_bruto, filho_corrigido


def mutacao(individuo):
    """Substitui 1 posição aleatória por número fora da lista."""
    mutado = individuo.copy()
    pos = random.randrange(len(mutado))
    valor_antigo = mutado[pos]
    disponiveis = [n for n in range(1, 21) if n not in mutado]
    if not disponiveis:
        return sorted(mutado), pos, valor_antigo, valor_antigo
    novo = random.choice(disponiveis)
    mutado[pos] = novo
    mutado.sort()
    return mutado, pos, valor_antigo, novo


def atualizar_populacao(populacao, aptidoes, filho, aptidao_filho):
    """Substitui o pior pela criança se for estritamente melhor (elitismo natural)."""
    indice_pior = min(range(len(populacao)), key=lambda i: aptidoes[i])
    aptidao_pior = aptidoes[indice_pior]
    if aptidao_filho > aptidao_pior:
        populacao[indice_pior] = filho
        aptidoes[indice_pior] = aptidao_filho
        return (f"Filho substituiu o indivíduo {indice_pior} "
                f"(aptidão {aptidao_pior} -> {aptidao_filho})"), indice_pior
    return (f"Filho descartado (aptidão {aptidao_filho} "
            f"<= pior aptidão {aptidao_pior})"), None


# =====================================================================
# LOOP PRINCIPAL DO AG
# =====================================================================

def _imprimir_populacao(populacao, aptidoes):
    print(f"  {'Idx':>3} | {'Indivíduo':<45} | Aptidão")
    print(f"  {'-'*3}-+-{'-'*45}-+--------")
    for i, (ind, apt) in enumerate(zip(populacao, aptidoes)):
        print(f"  {i:>3} | {str(ind):<45} | {apt:>5}")


def executar_ag(alvo, populacao_inicial=None, max_geracoes=100,
                limiar_estagnacao=20, seed=None):
    """Executa o Algoritmo Genético imprimindo cada etapa de cada geração."""
    if seed is not None:
        random.seed(seed)

    if populacao_inicial is None:
        populacao = gerar_populacao(20)
    else:
        assert len(populacao_inicial) == 20
        populacao = [sorted(ind) for ind in populacao_inicial]

    for ind in populacao:
        validar_individuo(ind)

    aptidoes = [calcular_aptidao(ind, alvo) for ind in populacao]
    melhor_aptidao_global = max(aptidoes)
    geracoes_sem_melhora = 0
    motivo_parada = "Limite máximo de gerações atingido"
    geracao_final = 0

    if melhor_aptidao_global == 10:
        idx = aptidoes.index(10)
        print("\n>>> Solução encontrada já na população inicial! <<<")
        return {
            "melhor_individuo": populacao[idx],
            "melhor_aptidao": 10,
            "geracoes_executadas": 0,
            "motivo_parada": "Aptidão máxima na população inicial",
        }

    for geracao in range(1, max_geracoes + 1):
        geracao_final = geracao
        print("\n" + "=" * 72)
        print(f"GERAÇÃO {geracao}")
        print("=" * 72)

        print("\n[1] AVALIAÇÃO DA POPULAÇÃO")
        _imprimir_populacao(populacao, aptidoes)

        idx_p1, c1 = torneio(populacao, aptidoes, k=2)
        idx_p2, c2 = torneio(populacao, aptidoes, k=2)
        pai1, pai2 = populacao[idx_p1], populacao[idx_p2]

        print("\n[2] SELEÇÃO POR TORNEIO (k=2)")
        print(f"  Torneio 1 -> concorrentes: índices {c1} "
              f"(aptidões {[aptidoes[i] for i in c1]})")
        print(f"             vencedor: índice {idx_p1} | Pai 1 = {pai1} "
              f"(aptidão {aptidoes[idx_p1]})")
        print(f"  Torneio 2 -> concorrentes: índices {c2} "
              f"(aptidões {[aptidoes[i] for i in c2]})")
        print(f"             vencedor: índice {idx_p2} | Pai 2 = {pai2} "
              f"(aptidão {aptidoes[idx_p2]})")

        filho_bruto, filho_apos_cruz = cruzamento(pai1, pai2)
        print("\n[3] CRUZAMENTO (corte na 5ª posição)")
        print(f"  Pai 1 (5 primeiros)  = {pai1[:5]}")
        print(f"  Pai 2 (5 últimos)    = {pai2[5:]}")
        print(f"  Filho bruto          = {filho_bruto}")
        print(f"  Filho após correção  = {filho_apos_cruz}")

        filho_mutado, pos_mut, val_a, val_n = mutacao(filho_apos_cruz)
        validar_individuo(filho_mutado)
        print("\n[4] MUTAÇÃO")
        print(f"  Posição sorteada     = {pos_mut}")
        print(f"  Substituição         = {val_a} -> {val_n}")
        print(f"  Filho após mutação   = {filho_mutado}")

        aptidao_filho = calcular_aptidao(filho_mutado, alvo)
        print("\n[5] AVALIAÇÃO DO FILHO")
        print(f"  Aptidão do filho     = {aptidao_filho}")

        acao, _ = atualizar_populacao(populacao, aptidoes,
                                      filho_mutado, aptidao_filho)
        print("\n[6] ATUALIZAÇÃO COM ELITISMO")
        print(f"  {acao}")

        melhor_ger = max(aptidoes)
        idx_melhor_ger = aptidoes.index(melhor_ger)
        print(f"\n  Melhor da geração: índice {idx_melhor_ger} = "
              f"{populacao[idx_melhor_ger]} | aptidão = {melhor_ger}")

        if melhor_ger > melhor_aptidao_global:
            melhor_aptidao_global = melhor_ger
            geracoes_sem_melhora = 0
        else:
            geracoes_sem_melhora += 1

        if melhor_ger == 10:
            motivo_parada = "Aptidão máxima (10) atingida"
            print(f"\n*** Critério de parada: {motivo_parada} ***")
            break
        if geracoes_sem_melhora >= limiar_estagnacao:
            motivo_parada = (f"Estagnação: {limiar_estagnacao} gerações "
                             f"sem melhora")
            print(f"\n*** Critério de parada: {motivo_parada} ***")
            break
    else:
        motivo_parada = f"Limite de {max_geracoes} gerações atingido"

    idx_final = max(range(len(populacao)), key=lambda i: aptidoes[i])
    print("\n" + "#" * 72)
    print("RESULTADO FINAL")
    print("#" * 72)
    print(f"Sequência-alvo (revelada):    {alvo}")
    print(f"Melhor indivíduo encontrado:  {populacao[idx_final]}")
    print(f"Aptidão final:                {aptidoes[idx_final]} / 10")
    print(f"Gerações executadas:          {geracao_final}")
    print(f"Motivo da parada:             {motivo_parada}")

    return {
        "melhor_individuo": populacao[idx_final],
        "melhor_aptidao": aptidoes[idx_final],
        "geracoes_executadas": geracao_final,
        "motivo_parada": motivo_parada,
    }


# =====================================================================
# INTERFACE GRÁFICA
# =====================================================================

class StreamParaFila(io.TextIOBase):
    """Stream thread-safe: enfileira; thread do Tk consome."""
    def __init__(self, fila):
        super().__init__()
        self.fila = fila

    def write(self, texto):
        if texto:
            self.fila.put(texto)
        return len(texto) if texto else 0

    def flush(self):
        pass


class JanelaPopulacaoManual(tk.Toplevel):
    """Janela modal para o usuário digitar os 20 indivíduos."""
    def __init__(self, master, populacao_atual=None):
        super().__init__(master)
        self.title("Inserir população inicial (20 indivíduos)")
        self.geometry("520x600")
        self.resultado = None

        ttk.Label(self,
                  text="Informe 10 números distintos em [1, 20] por linha "
                       "(separados por espaço ou vírgula):",
                  wraplength=480).pack(padx=10, pady=(10, 5), anchor="w")

        frame_lista = ttk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(frame_lista, highlightthickness=0)
        scroll = ttk.Scrollbar(frame_lista, orient="vertical",
                               command=canvas.yview)
        interno = ttk.Frame(canvas)
        interno.bind("<Configure>",
                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=interno, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.entries = []
        for i in range(20):
            linha = ttk.Frame(interno)
            linha.pack(fill="x", pady=2)
            ttk.Label(linha, text=f"Indivíduo {i+1:>2}:", width=12).pack(side="left")
            entry = ttk.Entry(linha, width=45)
            entry.pack(side="left", fill="x", expand=True)
            if populacao_atual and i < len(populacao_atual):
                entry.insert(0, " ".join(str(n) for n in populacao_atual[i]))
            self.entries.append(entry)

        frame_bot = ttk.Frame(self)
        frame_bot.pack(fill="x", padx=10, pady=10)
        ttk.Button(frame_bot, text="Preencher aleatoriamente",
                   command=self._preencher_aleatorio).pack(side="left")
        ttk.Button(frame_bot, text="Cancelar",
                   command=self.destroy).pack(side="right")
        ttk.Button(frame_bot, text="Confirmar",
                   command=self._confirmar).pack(side="right", padx=5)

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _preencher_aleatorio(self):
        for entry in self.entries:
            entry.delete(0, "end")
            entry.insert(0, " ".join(str(n) for n in gerar_individuo()))

    def _confirmar(self):
        populacao = []
        for i, entry in enumerate(self.entries):
            texto = entry.get().strip()
            try:
                numeros = [int(x) for x in texto.replace(",", " ").split()]
            except ValueError:
                messagebox.showerror("Erro",
                                     f"Indivíduo {i+1}: caracteres inválidos.")
                return
            if len(numeros) != 10 or len(set(numeros)) != 10 \
                    or not all(1 <= n <= 20 for n in numeros):
                messagebox.showerror("Erro",
                                     f"Indivíduo {i+1}: precisa de 10 "
                                     f"distintos em [1, 20].")
                return
            populacao.append(sorted(numeros))
        self.resultado = populacao
        self.destroy()


class InterfaceAG:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmo Genético — Simulação Didática")
        self.root.geometry("1050x720")
        self.populacao_manual = None
        self.thread_execucao = None
        self.fila_saida = queue.Queue()
        self._polling_id = None

        cfg = ttk.LabelFrame(root, text="Configuração", padding=10)
        cfg.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(cfg, text="Sequência-alvo:").grid(row=0, column=0, sticky="w", pady=3)
        self.var_alvo = tk.StringVar(value="aleatoria")
        ttk.Radiobutton(cfg, text="Aleatória", variable=self.var_alvo,
                        value="aleatoria").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(cfg, text="Manual:", variable=self.var_alvo,
                        value="manual").grid(row=0, column=2, sticky="w")
        self.entry_alvo = ttk.Entry(cfg, width=45)
        self.entry_alvo.grid(row=0, column=3, sticky="we", padx=5)
        self.entry_alvo.insert(0, "1 3 5 7 9 11 13 15 17 19")

        ttk.Label(cfg, text="População inicial:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_pop = tk.StringVar(value="aleatoria")
        ttk.Radiobutton(cfg, text="Aleatória", variable=self.var_pop,
                        value="aleatoria").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(cfg, text="Manual", variable=self.var_pop,
                        value="manual").grid(row=1, column=2, sticky="w")
        ttk.Button(cfg, text="Inserir 20 indivíduos...",
                   command=self.abrir_populacao_manual).grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(cfg, text="Máx. gerações:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_max = ttk.Entry(cfg, width=10)
        self.entry_max.grid(row=2, column=1, sticky="w")
        self.entry_max.insert(0, "100")

        ttk.Label(cfg, text="Limiar estagnação:").grid(row=2, column=2, sticky="w")
        self.entry_estag = ttk.Entry(cfg, width=10)
        self.entry_estag.grid(row=2, column=3, sticky="w", padx=5)
        self.entry_estag.insert(0, "20")

        cfg.columnconfigure(3, weight=1)

        bots = ttk.Frame(root)
        bots.pack(fill="x", padx=10, pady=5)
        self.btn_exec = ttk.Button(bots, text="▶ Executar AG", command=self.executar)
        self.btn_exec.pack(side="left")
        ttk.Button(bots, text="Limpar saída",
                   command=self.limpar).pack(side="left", padx=5)
        ttk.Button(bots, text="Salvar saída...",
                   command=self.salvar_saida).pack(side="left", padx=5)
        self.lbl_status = ttk.Label(bots, text="Pronto.", foreground="gray")
        self.lbl_status.pack(side="left", padx=15)

        saida = ttk.LabelFrame(root, text="Saída do Algoritmo", padding=5)
        saida.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.texto = scrolledtext.ScrolledText(saida, wrap="word",
                                               font=("Consolas", 9),
                                               state="disabled")
        self.texto.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    def abrir_populacao_manual(self):
        janela = JanelaPopulacaoManual(self.root, self.populacao_manual)
        if janela.resultado:
            self.populacao_manual = janela.resultado
            self.var_pop.set("manual")
            messagebox.showinfo("Sucesso",
                                "População manual com 20 indivíduos registrada.")

    def limpar(self):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.configure(state="disabled")

    def salvar_saida(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if caminho:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(self.texto.get("1.0", "end"))
            messagebox.showinfo("Salvo", f"Saída gravada em:\n{caminho}")

    def _ler_alvo(self):
        if self.var_alvo.get() == "manual":
            texto = self.entry_alvo.get().strip()
            try:
                numeros = [int(x) for x in texto.replace(",", " ").split()]
            except ValueError:
                raise ValueError("Sequência-alvo contém valores não inteiros.")
            if len(numeros) != 10 or len(set(numeros)) != 10 \
                    or not all(1 <= n <= 20 for n in numeros):
                raise ValueError(
                    "Sequência-alvo deve ter 10 inteiros distintos em [1, 20].")
            return sorted(numeros)
        return gerar_individuo()

    def _ler_int(self, entry, padrao, nome):
        texto = entry.get().strip()
        if not texto:
            return padrao
        try:
            return int(texto)
        except ValueError:
            raise ValueError(f"Valor inválido para {nome}: '{texto}'")

    def executar(self):
        if self.thread_execucao and self.thread_execucao.is_alive():
            messagebox.showwarning("Em execução",
                                   "Aguarde o término da execução atual.")
            return
        try:
            alvo = self._ler_alvo()
            max_ger = self._ler_int(self.entry_max, 100, "máx. gerações")
            limiar = self._ler_int(self.entry_estag, 20, "limiar estagnação")
        except ValueError as e:
            messagebox.showerror("Parâmetro inválido", str(e))
            return

        pop_inicial = None
        if self.var_pop.get() == "manual":
            if not self.populacao_manual or len(self.populacao_manual) != 20:
                messagebox.showerror(
                    "População manual ausente",
                    "Selecione 'Inserir 20 indivíduos...' e informe a população.")
                return
            pop_inicial = self.populacao_manual

        self.limpar()
        self.btn_exec.configure(state="disabled")
        self.lbl_status.configure(text="Executando...", foreground="blue")

        while not self.fila_saida.empty():
            try:
                self.fila_saida.get_nowait()
            except queue.Empty:
                break

        def alvo_thread():
            stream = StreamParaFila(self.fila_saida)
            stdout_original = sys.stdout
            sys.stdout = stream
            try:
                executar_ag(alvo=alvo, populacao_inicial=pop_inicial,
                            max_geracoes=max_ger, limiar_estagnacao=limiar)
            except Exception:
                import traceback
                print("\n\n*** ERRO durante a execução ***")
                traceback.print_exc(file=sys.stdout)
            finally:
                sys.stdout = stdout_original
                self.fila_saida.put(None)

        self.thread_execucao = threading.Thread(target=alvo_thread, daemon=True)
        self.thread_execucao.start()
        self._consumir_fila()

    def _consumir_fila(self):
        terminou = False
        pedacos = []
        try:
            while True:
                item = self.fila_saida.get_nowait()
                if item is None:
                    terminou = True
                    break
                pedacos.append(item)
        except queue.Empty:
            pass

        if pedacos:
            self.texto.configure(state="normal")
            self.texto.insert("end", "".join(pedacos))
            self.texto.see("end")
            self.texto.configure(state="disabled")

        if terminou:
            self.btn_exec.configure(state="normal")
            self.lbl_status.configure(text="Execução concluída.",
                                      foreground="green")
            self._polling_id = None
        else:
            self._polling_id = self.root.after(50, self._consumir_fila)


# =====================================================================
# ENTRADA — clique em Run
# =====================================================================

if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    InterfaceAG(root)
    root.mainloop()
