# Simulador de Algoritmo Genético

Simulação didática de um **Algoritmo Genético (AG)** com interface gráfica,
desenvolvida em Python puro (sem bibliotecas externas) para fins educativos.

O objetivo do AG é descobrir uma **sequência-alvo** secreta formada por
10 inteiros distintos no intervalo `[1, 20]`, em ordem crescente. A cada
geração, o programa imprime todas as etapas (avaliação, seleção, cruzamento,
mutação e atualização) para que se possa acompanhar o aprendizado do algoritmo.

---

## Como executar

1. Abra a pasta `algoritmo_genetico` no VS Code
   (*Arquivo → Abrir Pasta…*).
2. Abra o arquivo [`simulador_ag.py`](simulador_ag.py).
3. Pressione **F5** (ou clique em ▶ **Run**).
4. A janela da interface gráfica abre automaticamente.

> A configuração em `.vscode/` já aponta para o Python correto do sistema, então
> não é necessário escolher interpretador nem instalar nada.

---

## O que a interface permite

| Campo / botão | Função |
| --- | --- |
| **Sequência-alvo** | Definir o alvo aleatoriamente ou digitar manualmente os 10 números. |
| **População inicial** | Gerar aleatoriamente 20 indivíduos ou inserir manualmente em uma janela auxiliar. |
| **Máx. gerações** | Limite superior de iterações (padrão: 100). |
| **Limiar estagnação** | Encerra se o melhor indivíduo não melhorar por N gerações (padrão: 20). |
| ▶ **Executar AG** | Roda o algoritmo em uma thread separada, sem travar a interface. |
| **Limpar saída** | Apaga o conteúdo da área de log. |
| **Salvar saída…** | Exporta o log da execução em um arquivo `.txt`. |

---

## Especificação do algoritmo

### Representação
- Cada **indivíduo** é uma lista de **10 inteiros distintos** em `[1, 20]`, em
  ordem crescente.
- A **população** tem tamanho fixo de **20 indivíduos**.

### Função de aptidão
`fitness(individuo)` = quantidade de números do indivíduo que também aparecem
na sequência-alvo (posição irrelevante). Varia de **0 a 10**.

### Ciclo de cada geração
1. **Avaliação**: calcula a aptidão dos 20 indivíduos e exibe a tabela.
2. **Seleção por torneio (k = 2)**: dois torneios independentes; em cada um, 2
   indivíduos sorteados disputam e o de maior aptidão é eleito (Pai 1 e Pai 2).
3. **Cruzamento (corte na 5ª posição)**:
   - `filho_bruto` = 5 primeiros do Pai 1 + 5 últimos do Pai 2.
   - Duplicatas são substituídas por números aleatórios ainda não presentes.
   - O filho é reordenado em ordem crescente.
4. **Mutação**: uma posição aleatória é trocada por um número que ainda não
   está no indivíduo. Reordena.
5. **Avaliação do filho**: calcula sua aptidão.
6. **Atualização com elitismo**: o filho substitui o **pior** indivíduo apenas
   se for **estritamente melhor** — assim o melhor da geração é sempre
   preservado.

### Critérios de parada
- Algum indivíduo atinge aptidão **10** (sequência encontrada).
- **Máximo de gerações** atingido.
- **Estagnação**: N gerações consecutivas sem melhora no melhor indivíduo.

---

## Estrutura do código

O arquivo `simulador_ag.py` está dividido em blocos claros:

| Bloco | Funções |
| --- | --- |
| Representação | `gerar_individuo`, `gerar_populacao`, `validar_individuo` |
| Aptidão | `calcular_aptidao` |
| Operadores genéticos | `torneio`, `cruzamento`, `mutacao`, `atualizar_populacao` |
| Loop principal | `executar_ag` |
| Interface gráfica | `InterfaceAG`, `JanelaPopulacaoManual`, `StreamParaFila` |

Toda a saída textual gerada por `executar_ag` (impressa via `print`) é
**redirecionada** para a área de texto da interface por meio de uma fila
thread-safe (`queue.Queue`), de modo que o AG roda em segundo plano sem
congelar a janela.

---

## Requisitos

- **Python 3.10 ou superior** (testado em **Python 3.12**).
- Sistema operacional: **Windows / macOS / Linux**.
- Bibliotecas: apenas as do **núcleo padrão** — `random`, `tkinter`, `queue`,
  `threading`, `io`, `sys`.

---

## Solução de problemas

| Problema | Causa provável | Solução |
| --- | --- | --- |
| "Python não foi encontrado" ao dar Run | Comando `python` no PATH aponta para o stub da Microsoft Store. | Em *Configurações → Aliases de execução do aplicativo*, desligar `python.exe` e `python3.exe`. |
| Acentos quebrados no terminal | Console em CP-1252 no Windows. | O próprio script já força UTF-8 (`sys.stdout.reconfigure`). |
| Janela não abre | `tkinter` ausente (raro). | Reinstalar Python marcando *"tcl/tk and IDLE"*. |

---

## Licença e uso

Material didático livre para uso em sala de aula, estudos e adaptações.
