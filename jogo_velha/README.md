# Jogo da Velha 4×4 com Minimax + Poda Alfa-Beta

Implementação didática de um **agente de IA invencível** para uma versão
expandida do Jogo da Velha (tabuleiro **4×4**, vence quem alinhar **4**
símbolos), desenvolvida em **Python puro** (sem bibliotecas externas) para
a disciplina de Inteligência Artificial.

O agente usa **busca competitiva (adversarial search)** com o algoritmo
**Minimax + poda alfa-beta**, profundidade limitada e função heurística de
avaliação. Interface gráfica em **Tkinter** (já vem no Python — nada a
instalar).

---

## Como executar

1. Abra a pasta `jogo_velha` no VS Code
   (*Arquivo → Abrir Pasta…*).
2. Abra o arquivo [`jogo_velha_4x4_vscode.py`](jogo_velha_4x4_vscode.py).
3. Pressione **F5** (ou clique em ▶ **Run**) — ou rode no terminal:

   ```bash
   python jogo_velha_4x4_vscode.py
   ```
   No Windows, se `python` não funcionar, tente `py jogo_velha_4x4_vscode.py`.
4. A janela do jogo abre automaticamente.

> Você joga com **X**, a IA joga com **O**. Clique numa casa vazia para
> fazer sua jogada; a IA responde em seguida e atualiza os indicadores
> de desempenho.

---

## O que a interface mostra

| Elemento | Função |
| --- | --- |
| **Tabuleiro 4×4** | Botões clicáveis. X em ciano, O em vermelho. |
| **Última jogada da IA** | Destacada em **amarelo** (fica fácil acompanhar). |
| **Linha vencedora** | Destacada em **verde** ao final do jogo. |
| **Status** | Indica de quem é a vez, "IA pensando…", ou o resultado. |
| **Painel de indicadores** | Nós avaliados, cortes alfa-beta, tempo, melhor jogada. |
| ▶ **Reiniciar Jogo** | Limpa o tabuleiro e zera os indicadores. |
| **Sair** | Encerra o programa. |

---

## Especificação do algoritmo

### Representação
- **Tabuleiro**: matriz 4×4 (lista de listas) com `'X'`, `'O'` ou `' '`.
- **Linhas vencedoras**: pré-computadas — 4 horizontais + 4 verticais +
  2 diagonais = **10 linhas**.

### Estados terminais
- Vitória do agente (`O`): valor **+10⁶ − profundidade** (prefere vencer rápido).
- Vitória do humano (`X`): valor **−10⁶ + profundidade** (adia derrota).
- Empate (tabuleiro cheio sem vencedor): **0**.

### Função heurística (cortes por profundidade)
Para cada uma das 10 linhas vencedoras:

| Conteúdo da linha | Pontuação |
| --- | --- |
| Tem **X e O** simultaneamente | **0** (linha morta, ninguém vence por ela) |
| Apenas `O` — 1, 2 ou 3 símbolos | **+1**, **+10**, **+100** |
| Apenas `X` — 1, 2 ou 3 símbolos | **−1**, **−10**, **−100** |

O crescimento **exponencial** (1 / 10 / 100) faz a IA priorizar
bloquear/criar ameaças avançadas (3 em linha) sobre melhorar linhas fracas
— comportamento agressivo e defensivo sem regras adicionais.

### Minimax com poda alfa-beta
- `alfa` = melhor valor já garantido para **MAX** (a IA) até aqui.
- `beta` = melhor valor já garantido para **MIN** (o humano) até aqui.
- Quando `alfa >= beta`, o adversário **acima** na árvore nunca permitiria
  o jogo cair naquele ramo — então abandonar os irmãos **não pode** alterar
  o valor que sobe até a raiz. A poda **preserva a decisão** do Minimax
  puro, apenas reduzindo o número de nós visitados.
- Para potencializar a poda, os movimentos são **ordenados pelas casas
  centrais primeiro** (`move ordering`): jogadas fortes tendem a aparecer
  cedo, gerando cortes mais cedo.

### Profundidade limitada
- Constante `PROFUNDIDADE = 4` no topo do arquivo (ajustável: **4 a 6**).
- Necessária porque o espaço de estados do 4×4 (até 16! posições) é
  grande demais para busca exaustiva em tempo razoável.
- Quando a busca atinge a profundidade limite sem estado terminal, usa-se
  a **heurística** acima para estimar o valor.

---

## Estrutura do código

O arquivo `jogo_velha_4x4_vscode.py` está dividido em blocos claros:

| Bloco | Funções |
| --- | --- |
| Constantes | `JOGADOR_X`, `JOGADOR_O`, `TAMANHO`, `PROFUNDIDADE` |
| Métricas | classe `Metricas` |
| Tabuleiro | `inicializar_tabuleiro`, `obter_movimentos_validos`, `tabuleiro_cheio` |
| Detecção de vitória | `_gerar_linhas_vencedoras`, `verificar_vencedor` |
| Heurística | `avaliar_heuristica` |
| Busca | `minimax`, `encontrar_melhor_jogada` |
| Interface gráfica | classe `JogoVelhaApp` |

---

## Indicadores de desempenho (atendem ao enunciado)

Após cada jogada da IA, o painel inferior mostra:

| Indicador | Descrição |
| --- | --- |
| **Número de nós avaliados** | Total de chamadas a `minimax` (= estados visitados). |
| **Cortes alfa-beta** | Quantas vezes a poda interrompeu a iteração de irmãos. |
| **Tempo de execução** | Tempo total para escolher a jogada (em segundos). |
| **Melhor jogada** | Coordenada `(linha, coluna)` escolhida + escore minimax. |

> **Como saber se a poda está ativa?** Se "Cortes alfa-beta" for maior
> que **0**, a poda cortou algum ramo nessa jogada. É comum ver dezenas
> ou centenas de cortes já nas primeiras jogadas com `PROFUNDIDADE = 4`.

---

## Por que o agente é (praticamente) invencível

- O **Minimax** assume oponente ótimo: escolhe sempre a jogada que
  **maximiza o pior caso** — então, contra qualquer estratégia, o
  resultado da IA é pelo menos tão bom quanto o do jogo perfeito visto
  dentro do horizonte da busca.
- A **heurística exponencial** garante que bloquear `3-em-linha` do
  humano e construir *forks* (duas ameaças simultâneas) sempre dominem
  outras escolhas — exatamente as situações que decidem o jogo.
- Resultado prático: até `PROFUNDIDADE = 4`, a IA **não perde** contra um
  humano comum em testes informais — no máximo empata.

### Limites da garantia no 4×4

- **Não há prova fechada** de que o 4×4-4 termina sempre em empate com
  jogo perfeito (diferente do 3×3-3, que é provadamente empate). A
  árvore tem ordem de 16! ≈ 2×10¹³ estados — inviável esgotar num PC.
- **Efeito horizonte**: como usamos profundidade limitada, uma ameaça
  que só se revela **depois** do corte pode passar despercebida. Subir
  `PROFUNDIDADE` para 5 ou 6 mitiga o problema (a poda alfa-beta torna
  isso viável em segundos).
- A qualidade depende fortemente da **heurística** e da **profundidade**;
  a invencibilidade aqui é **empírica**, não teorema.

---

## Sobre a poda alfa-beta — esclarecimento importante

A poda **não descarta** ramos "com menos chance de ganhar". Ela descarta
apenas ramos **comprovadamente irrelevantes** para a decisão final —
aqueles em que o adversário (acima na árvore) **nunca permitiria** o jogo
cair, porque já tem uma alternativa melhor garantida em outro lugar.

> A jogada escolhida pela IA é **exatamente a mesma** que o Minimax sem
> poda escolheria. A poda só reduz o **trabalho computacional**, não a
> qualidade da decisão. Na ordem de jogadas ideal, a complexidade cai
> de **O(b^d)** para **O(b^(d/2))** — o que dobra a profundidade
> alcançável no mesmo tempo.

---

## Requisitos

- **Python 3.10 ou superior** (testado em **Python 3.12**).
- Sistema operacional: **Windows / macOS / Linux**.
- Bibliotecas: apenas as do **núcleo padrão** — `math`, `time`, `tkinter`.

---

## Solução de problemas

| Problema | Causa provável | Solução |
| --- | --- | --- |
| "Python não foi encontrado" ao dar Run | Comando `python` no PATH aponta para o stub da Microsoft Store. | Em *Configurações → Aliases de execução do aplicativo*, desligar `python.exe` e `python3.exe`, ou usar `py` no lugar de `python`. |
| Janela não abre | `tkinter` ausente (raro no Windows/Mac, comum em Linux mínimo). | Linux: `sudo apt install python3-tk`. Windows/Mac: reinstalar Python marcando *"tcl/tk and IDLE"*. |
| IA demora muito a jogar | Profundidade alta demais. | Reduzir `PROFUNDIDADE` (no topo do `.py`) de 6 para 5 ou 4. |
| Quero uma IA mais forte | Profundidade baixa. | Aumentar `PROFUNDIDADE` para 5 ou 6 (custo cresce ≈ exponencialmente, mas a poda segura). |

---

## Licença e uso

Material didático livre para uso em sala de aula, estudos e adaptações.
