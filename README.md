# 📊 Análise exploratória do catálogo da Netflix

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=flat-square)

Primeiro projeto de análise de dados feito **ao vivo, com IA como copiloto**, na palestra *"Análise de dados com IA: do zero ao primeiro projeto de portfólio"*.

> [!NOTE]
> **Sobre a palestra.** Apresentei online em agosto de 2026 para cerca de 25 estudantes do 1º período de Análise e Desenvolvimento de Sistemas de um Instituto Federal e para cerca de 20 participantes da comunidade **STEM Girls**. O objetivo foi mostrar o caminho que eu gostaria de ter tido no meu primeiro projeto: do zero até um repositório organizado no GitHub. Este repositório é o projeto que construímos juntos.

---

## 🧭 O passo a passo da palestra

| # | Etapa | Ferramenta |
|---|---|---|
| 1 | Instalar a IDE com agente de IA e ativar o plano gratuito para estudantes | Google Antigravity |
| 2 | Criar a conta e o primeiro repositório | GitHub |
| 3 | Clonar o repositório para a máquina | Git |
| 4 | Pedir ajuda para formular as perguntas de análise | ChatGPT |
| 5 | Baixar um dataset público e colocar no projeto | Kaggle |
| 6 | Ativar o agente do GitHub Copilot | GitHub Copilot |
| 7 | Pedir ao agente que responda às perguntas com os dados | Antigravity |
| 8 | Ler e conferir o código gerado | Pandas, NumPy, Matplotlib, Seaborn |
| 9 | Escrever um README que explique o projeto | Markdown |
| 10 | Fazer commit e push e ver como o projeto aparece no GitHub | Git e GitHub |

Os prompts usados estão em [`ai_logs.md`](./ai_logs.md).

---

## ⚠️ A lição mais importante: conferir o que a IA escreveu

A primeira versão deste README foi escrita pela IA e **parecia ótima**. Quando rodei o código e comparei com os dados, várias frases não se sustentavam:

| A IA escreveu | O que os dados mostram |
|---|---|
| "Japão e Coreia do Sul estão entre os 5 primeiros países" | Japão é o 6º e Coreia do Sul o 8º. O top 5 é EUA, Índia, Reino Unido, Canadá e França |
| "Brasil e México representam a América Latina no ranking" | O Brasil **não está** no top 10. Só o México aparece, em 10º |
| "Janeiro tem volume expressivo e março a maio têm menos adições" | Janeiro, março e abril ficam na média. O mês mais fraco é fevereiro |

Os números calculados pelo código estavam certos. O erro estava nas **frases em volta deles**, que a IA completou com o que "parecia provável". Por isso, a análise abaixo foi reescrita só com o que o código calcula, e as explicações de negócio aparecem como **hipóteses**, não como fatos.

**Regra que levo para todo projeto:** a IA acelera, mas cada afirmação do README precisa apontar para um número que o código gerou.

---

## 📁 Estrutura

```
projeto-analise-dados/
├── analise_netflix.py   # script com as 6 análises
├── netflix_titles.csv   # dataset (Kaggle, domínio público)
├── graficos/            # um gráfico por pergunta, gerado pelo script
├── ai_logs.md           # prompts usados na palestra
└── requirements.txt
```

## 🗂️ Dataset

| | |
|---|---|
| **Fonte** | [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows), de Shivam Bansal, no Kaggle |
| **Licença** | CC0: domínio público |
| **Tamanho** | 8.807 títulos (8.804 após a limpeza) e 12 colunas |
| **Período** | títulos adicionados entre 2008 e setembro de 2021 |

**Limpeza:** em 3 linhas a duração ("74 min") estava na coluna de classificação indicativa por engano; essas linhas foram removidas.

---

## 📈 Análises

### 1. Como a divisão entre filmes e séries evoluiu?
![Filmes vs. séries](./graficos/q1_evolucao_filmes_series.png)

- O catálogo cresceu de verdade a partir de **2016**. O pico foi **2019, com 2.016 títulos adicionados**.
- **Filmes são maioria em todos os anos com volume relevante.** Em 2021 foram 66,3% dos títulos adicionados.
- Antes de 2016 entraram menos de 100 títulos por ano, então as oscilações de proporção desse período não dizem muito.
- 2021 só tem dados até setembro: a queda nesse ano não deve ser lida como retração.

### 2. Quais países têm mais títulos?
![Top 10 países](./graficos/q2_top10_paises.png)

- **Estados Unidos lideram com 3.687 títulos, 36,8%** das menções de país, mais que o triplo da **Índia** (1.046), em 2º.
- Completam o top 5: Reino Unido, Canadá e França. Japão, Espanha, Coreia do Sul, Alemanha e México fecham o top 10.
- Coproduções contam uma vez para cada país, então a soma passa do número de títulos.

### 3. Quais gêneros aparecem mais?
![Gêneros](./graficos/q3_generos_frequentes.png)

- **International Movies** lidera com **2.752 títulos**, seguido de Dramas (2.427) e Comedies (1.674).
- International TV Shows (1.351) e Documentaries (869) completam o top 5.
- Cada título pode ter até 3 gêneros, por isso a contagem é por gênero, não por título.

### 4. Para que público é o catálogo?
![Classificação indicativa](./graficos/q4_classificacoes_rating.png)

- **TV-MA**, conteúdo adulto, é a classificação mais comum (3.207 títulos), seguida de TV-14 (2.160).
- Somando TV-MA, R e NC-17, o **conteúdo adulto é 45,6%** do catálogo.

### 5. Em que meses entram mais títulos?
![Sazonalidade](./graficos/q5_sazonalidade_mensal.png)

- **Julho é o mês com mais adições (827)**, com dezembro logo atrás (813).
- **Fevereiro é o mais fraco (563)**, mas também é o mês mais curto. Os demais meses ficam entre 630 e 770.
- Filmes e séries seguem o mesmo desenho ao longo do ano.

### 6. Quantas séries ficam na 1ª temporada?
![Temporadas](./graficos/q6_series_temporadas.png)

- **67,0% das séries têm só 1 temporada** (1.793 de 2.676).
- 425 têm 2 temporadas e 199 têm 3. Só 43 chegam a 8 ou mais.
- O dataset não diz se a série foi cancelada, se é minissérie ou se só a 1ª temporada foi licenciada. Por isso, este número sozinho não prova que "a Netflix cancela muito".

---

## 🔍 Limitações e próximas análises

- **É uma foto do catálogo até setembro de 2021.** Não mostra o que é mais assistido nem a diferença entre os catálogos de cada país.
- **Hipóteses para testar com outros dados:**
  - O pico de 2019 coincide com a chegada do Disney+ e da Apple TV+. Houve reação da Netflix? Precisaria de dados de lançamento dos concorrentes e de investimento.
  - As séries de 1 temporada foram canceladas ou planejadas assim? Precisaria separar originais Netflix de licenciadas.
  - A coluna `description` permite análise de texto (temas mais comuns por ano ou gênero).

---

## ▶️ Como rodar

```bash
git clone https://github.com/byluxp/projeto-analise-dados.git
cd projeto-analise-dados

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python analise_netflix.py
```

Os gráficos são gerados na pasta `graficos/`.

---

Feito por **Lucila Vitória** · [LinkedIn](https://www.linkedin.com/in/lucila-cardoso/) · [GitHub](https://github.com/byluxp)
