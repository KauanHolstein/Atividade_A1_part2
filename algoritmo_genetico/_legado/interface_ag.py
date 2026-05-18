"""
Interface Gráfica (Tkinter) para a Simulação de Algoritmo Genético
------------------------------------------------------------------
Permite testar o AG visualmente, configurando todos os parâmetros
e acompanhando a saída geração a geração em uma área de texto rolável.

Execução: python interface_ag.py
"""

import io
import queue
import sys
import threading
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog

import algoritmo_genetico as ag


# =====================================================================
# Janela auxiliar para inserir os 20 indivíduos da população manual
# =====================================================================

class JanelaPopulacaoManual(tk.Toplevel):
    """Janela modal para o usuário digitar os 20 indivíduos da população."""

    def __init__(self, master, populacao_atual=None):
        super().__init__(master)
        self.title("Inserir população inicial (20 indivíduos)")
        self.geometry("520x600")
        self.resultado = None

        ttk.Label(
            self,
            text="Informe 10 números distintos em [1, 20] por linha "
                 "(separados por espaço ou vírgula):",
            wraplength=480,
        ).pack(padx=10, pady=(10, 5), anchor="w")

        # Área de entrada com 20 campos
        frame_lista = ttk.Frame(self)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(frame_lista, highlightthickness=0)
        scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
        interno = ttk.Frame(canvas)
        interno.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
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

        # Botões
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
            entry.insert(0, " ".join(str(n) for n in ag.gerar_individuo()))

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
            if len(numeros) != 10:
                messagebox.showerror("Erro",
                                     f"Indivíduo {i+1}: precisa ter 10 números.")
                return
            if len(set(numeros)) != 10:
                messagebox.showerror("Erro",
                                     f"Indivíduo {i+1}: números devem ser distintos.")
                return
            if not all(1 <= n <= 20 for n in numeros):
                messagebox.showerror("Erro",
                                     f"Indivíduo {i+1}: valores devem estar em [1, 20].")
                return
            populacao.append(sorted(numeros))
        self.resultado = populacao
        self.destroy()


# =====================================================================
# Stream que redireciona stdout para o widget Text de forma segura
# =====================================================================

class StreamParaFila(io.TextIOBase):
    """Stream que apenas enfileira o texto recebido — thread-safe.
    A thread principal do Tk consome a fila via polling (após after())."""

    def __init__(self, fila):
        super().__init__()
        self.fila = fila

    def write(self, texto):
        if texto:
            self.fila.put(texto)
        return len(texto) if texto else 0

    def flush(self):
        pass


# =====================================================================
# Janela principal
# =====================================================================

class InterfaceAG:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmo Genético - Simulação Didática")
        self.root.geometry("1050x720")
        self.populacao_manual = None
        self.thread_execucao = None
        self.fila_saida = queue.Queue()
        self._polling_id = None

        # ---------- Configuração ----------
        cfg = ttk.LabelFrame(root, text="Configuração", padding=10)
        cfg.pack(fill="x", padx=10, pady=(10, 5))

        # --- Sequência-alvo ---
        ttk.Label(cfg, text="Sequência-alvo:").grid(row=0, column=0, sticky="w", pady=3)
        self.var_alvo = tk.StringVar(value="aleatoria")
        ttk.Radiobutton(cfg, text="Aleatória", variable=self.var_alvo,
                        value="aleatoria").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(cfg, text="Manual:", variable=self.var_alvo,
                        value="manual").grid(row=0, column=2, sticky="w")
        self.entry_alvo = ttk.Entry(cfg, width=45)
        self.entry_alvo.grid(row=0, column=3, sticky="we", padx=5)
        self.entry_alvo.insert(0, "1 3 5 7 9 11 13 15 17 19")

        # --- População inicial ---
        ttk.Label(cfg, text="População inicial:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_pop = tk.StringVar(value="aleatoria")
        ttk.Radiobutton(cfg, text="Aleatória", variable=self.var_pop,
                        value="aleatoria").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(cfg, text="Manual",  variable=self.var_pop,
                        value="manual").grid(row=1, column=2, sticky="w")
        ttk.Button(cfg, text="Inserir 20 indivíduos...",
                   command=self.abrir_populacao_manual).grid(row=1, column=3, sticky="w", padx=5)

        # --- Parâmetros numéricos ---
        ttk.Label(cfg, text="Máx. gerações:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_max = ttk.Entry(cfg, width=10)
        self.entry_max.grid(row=2, column=1, sticky="w")
        self.entry_max.insert(0, "100")

        ttk.Label(cfg, text="Limiar estagnação:").grid(row=2, column=2, sticky="w")
        self.entry_estag = ttk.Entry(cfg, width=10)
        self.entry_estag.grid(row=2, column=3, sticky="w", padx=5)
        self.entry_estag.insert(0, "20")

        ttk.Label(cfg, text="Seed (opcional):").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_seed = ttk.Entry(cfg, width=10)
        self.entry_seed.grid(row=3, column=1, sticky="w")
        self.entry_seed.insert(0, "42")

        cfg.columnconfigure(3, weight=1)

        # ---------- Botões ----------
        bots = ttk.Frame(root)
        bots.pack(fill="x", padx=10, pady=5)
        self.btn_exec = ttk.Button(bots, text="▶ Executar AG", command=self.executar)
        self.btn_exec.pack(side="left")
        ttk.Button(bots, text="Limpar saída", command=self.limpar).pack(side="left", padx=5)
        ttk.Button(bots, text="Salvar saída...",
                   command=self.salvar_saida).pack(side="left", padx=5)
        self.lbl_status = ttk.Label(bots, text="Pronto.", foreground="gray")
        self.lbl_status.pack(side="left", padx=15)

        # ---------- Saída ----------
        saida = ttk.LabelFrame(root, text="Saída do Algoritmo", padding=5)
        saida.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.texto = scrolledtext.ScrolledText(
            saida, wrap="word", font=("Consolas", 9), state="disabled"
        )
        self.texto.pack(fill="both", expand=True)

    # -----------------------------------------------------------------
    # Ações da interface
    # -----------------------------------------------------------------

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
        from tkinter import filedialog
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )
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
                    "Sequência-alvo deve ter 10 inteiros distintos em [1, 20]."
                )
            return sorted(numeros)
        return ag.gerar_individuo()

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

        # --- Validação dos parâmetros ---
        try:
            alvo = self._ler_alvo()
            max_ger = self._ler_int(self.entry_max, 100, "máx. gerações")
            limiar = self._ler_int(self.entry_estag, 20, "limiar estagnação")
            seed_txt = self.entry_seed.get().strip()
            seed = int(seed_txt) if seed_txt else None
        except ValueError as e:
            messagebox.showerror("Parâmetro inválido", str(e))
            return

        pop_inicial = None
        if self.var_pop.get() == "manual":
            if not self.populacao_manual or len(self.populacao_manual) != 20:
                messagebox.showerror(
                    "População manual ausente",
                    "Selecione 'Inserir 20 indivíduos...' e informe a população."
                )
                return
            pop_inicial = self.populacao_manual

        # --- Prepara saída ---
        self.limpar()
        self.btn_exec.configure(state="disabled")
        self.lbl_status.configure(text="Executando...", foreground="blue")

        # Esvazia fila residual de execuções anteriores
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
                ag.executar_ag(
                    alvo=alvo,
                    populacao_inicial=pop_inicial,
                    max_geracoes=max_ger,
                    limiar_estagnacao=limiar,
                    seed=seed,
                )
            except Exception:
                import traceback
                print("\n\n*** ERRO durante a execução ***")
                traceback.print_exc(file=sys.stdout)
            finally:
                sys.stdout = stdout_original
                # Sentinela indica fim para a thread principal
                self.fila_saida.put(None)

        self.thread_execucao = threading.Thread(target=alvo_thread, daemon=True)
        self.thread_execucao.start()
        # Inicia o consumidor da fila na thread principal
        self._consumir_fila()

    def _consumir_fila(self):
        """Roda na thread principal; drena a fila para o widget."""
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
# Entrada
# =====================================================================

if __name__ == "__main__":
    root = tk.Tk()
    try:
        # Tema mais moderno se disponível
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    InterfaceAG(root)
    root.mainloop()
