"""
=============================================================================
ANÁLISE EXPLORATÓRIA DO CATÁLOGO NETFLIX
=============================================================================
Autor   : Analista de Dados
Dataset : netflix_titles.csv  (8.807 títulos)
Libs    : pandas · numpy · seaborn · matplotlib
Objetivo: Responder 6 perguntas-chave sobre o catálogo da plataforma e
          gerar visualizações prontas para relatório.

Nota técnica: matplotlib.use("Agg") é obrigatório em ambientes sem
display X11. Deve ser chamado ANTES de qualquer import de matplotlib.
=============================================================================
"""

# ---------------------------------------------------------------------------
# 0. IMPORTAÇÕES — ordem importa: Agg antes de qualquer plt
# ---------------------------------------------------------------------------
import os
import warnings

import matplotlib
matplotlib.use("Agg")   # backend não-interativo: salva em arquivo sem GUI

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 1. CONFIGURAÇÕES GLOBAIS DE ESTILO
# ---------------------------------------------------------------------------
# Paleta inspirada na identidade visual da Netflix (vermelho + tons escuros)
NETFLIX_RED  = "#E50914"
NETFLIX_DARK = "#141414"

sns.set_theme(
    style="darkgrid",
    rc={
        "figure.facecolor": NETFLIX_DARK,
        "axes.facecolor":   "#1e1e1e",
        "axes.edgecolor":   "#333333",
        "axes.labelcolor":  "#e0e0e0",
        "xtick.color":      "#cccccc",
        "ytick.color":      "#cccccc",
        "grid.color":       "#2a2a2a",
        "grid.linewidth":   0.6,
        "text.color":       "#e0e0e0",
        "font.family":      "DejaVu Sans",
    },
)

OUTPUT_DIR = "graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. CARREGAMENTO E LIMPEZA DOS DADOS
# ---------------------------------------------------------------------------
def carregar_e_limpar(caminho: str) -> pd.DataFrame:
    """
    Lê o CSV e aplica tratamentos de qualidade antes das análises.

    Tratamentos:
    - date_added  → datetime; extrai year_added e month_added
    - rating      → remove linhas onde o valor é duração em minutos (erro)
    """
    df = pd.read_csv(caminho)

    # Converte date_added para datetime e extrai componentes temporais
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"]  = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    # Remove registros onde 'rating' contém uma duração (ex: "74 min") — erro na origem
    mask_errado = df["rating"].str.contains(r"\d+ min", na=False)
    df = df[~mask_errado].copy()

    return df


df = carregar_e_limpar("netflix_titles.csv")

print(f"Dataset carregado: {len(df):,} registros | {df.shape[1]} colunas")
print(f"Periodo de adicao: {int(df['year_added'].min())} a {int(df['year_added'].max())}\n")


# ---------------------------------------------------------------------------
# FUNÇÃO AUXILIAR: salvar figura
# ---------------------------------------------------------------------------
def salvar(fig: plt.Figure, nome: str):
    """Salva a figura em alta resolução na pasta de saída (graficos/)."""
    caminho = os.path.join(OUTPUT_DIR, nome)
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  Salvo -> {caminho}")


# ===========================================================================
# PERGUNTA 1 — Evolução de Filmes vs. Séries ao longo dos anos
# ===========================================================================
def analise_q1(df: pd.DataFrame):
    """
    Agrupa por ano de adição e tipo (Movie / TV Show), calcula proporção
    percentual anual e plota:
      - Subplot 1: área empilhada (proporção %)
      - Subplot 2: barras agrupadas (volume absoluto)

    Por que dois subplots?
      Proporção revela ESTRATÉGIA; volume absoluto revela CRESCIMENTO.
    """
    print("Q1 - Evolucao filmes vs. series ao longo dos anos")

    sub = df.dropna(subset=["year_added"]).copy()
    sub = sub[sub["year_added"] >= 2008].copy()  # Netflix streaming desde 2007

    # Contagem por ano e tipo
    contagem = (
        sub.groupby(["year_added", "type"])
        .size()
        .reset_index(name="count")
    )

    # Proporção percentual por ano
    total_ano = contagem.groupby("year_added")["count"].transform("sum")
    contagem["pct"] = (contagem["count"] / total_ano * 100).round(1)

    # Pivot: linhas = anos, colunas = tipo
    pivot_pct = contagem.pivot(index="year_added", columns="type", values="pct").fillna(0)
    pivot_abs = contagem.pivot(index="year_added", columns="type", values="count").fillna(0)

    anos  = pivot_pct.index.astype(int).tolist()
    tipos = pivot_pct.columns.tolist()
    cores = {"Movie": NETFLIX_RED, "TV Show": "#aaaaaa"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=False,
                                    gridspec_kw={"hspace": 0.45})
    fig.patch.set_facecolor(NETFLIX_DARK)

    # --- Subplot 1: área empilhada (proporção) ---
    acumulado = np.zeros(len(anos))
    for tipo in tipos:
        vals = pivot_pct[tipo].values if tipo in pivot_pct.columns else np.zeros(len(anos))
        ax1.fill_between(anos, acumulado, acumulado + vals,
                         color=cores.get(tipo, "#888"), alpha=0.85, label=tipo)
        acumulado += vals

    ax1.set_ylim(0, 100)
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax1.set_ylabel("Participacao (%)", fontsize=11)
    ax1.set_title("Evolucao da Distribuicao — Filmes vs. Series (proporção %)",
                  fontsize=13, fontweight="bold", color="white", pad=10)
    ax1.legend(title="Tipo", framealpha=0.3, facecolor="#222",
               edgecolor="#555", labelcolor="white", title_fontsize=9)
    ax1.axvline(x=2015, color="#ffcc00", linewidth=1.2, linestyle="--", alpha=0.8)
    ax1.text(2015.1, 88, "Expansao de Series", color="#ffcc00", fontsize=8, va="top")
    ax1.set_xticks(anos)
    ax1.tick_params(axis="x", rotation=45)

    # --- Subplot 2: barras agrupadas (volume absoluto) ---
    x   = np.arange(len(anos))
    w   = 0.35
    n_t = len(tipos)
    for i, tipo in enumerate(tipos):
        vals = pivot_abs[tipo].values if tipo in pivot_abs.columns else np.zeros(len(anos))
        offset = (i - (n_t - 1) / 2) * w
        ax2.bar(x + offset, vals, width=w, label=tipo,
                color=cores.get(tipo, "#888"), alpha=0.9)

    ax2.set_xticks(x)
    ax2.set_xticklabels([str(a) for a in anos], rotation=45, ha="right")
    ax2.set_ylabel("Qtd. Titulos Adicionados", fontsize=11)
    ax2.set_xlabel("Ano de Adicao a Plataforma", fontsize=11)
    ax2.set_title("Volume Absoluto de Titulos por Ano",
                  fontsize=13, fontweight="bold", color="white", pad=10)
    ax2.legend(title="Tipo", framealpha=0.3, facecolor="#222",
               edgecolor="#555", labelcolor="white", title_fontsize=9)

    plt.tight_layout()
    salvar(fig, "q1_evolucao_filmes_series.png")
    plt.close(fig)

    ultimo_ano = int(pivot_pct.index.max())
    pct_movie = pivot_pct.loc[ultimo_ano, "Movie"] if "Movie" in pivot_pct.columns else 0
    pct_show  = pivot_pct.loc[ultimo_ano, "TV Show"] if "TV Show" in pivot_pct.columns else 0
    print(f"  Ultimo ano ({ultimo_ano}): Filmes={pct_movie:.1f}% | Series={pct_show:.1f}%\n")
    return contagem


# ===========================================================================
# PERGUNTA 2 — Top 10 países produtores de conteúdo
# ===========================================================================
def analise_q2(df: pd.DataFrame):
    """
    Expande países múltiplos (ex: 'USA, Brazil') em linhas individuais via
    str.split + explode, depois conta e calcula participação percentual.

    Um título com múltiplos países é contado para cada um deles,
    refletindo co-produções internacionais — comportamento esperado.
    """
    print("Q2 - Top 10 paises produtores de conteudo")

    paises = (
        df["country"]
        .dropna()
        .str.split(", ")
        .explode()
        .str.strip()
    )

    contagem = paises.value_counts().head(10).reset_index()
    contagem.columns = ["country", "count"]
    contagem["pct"] = (contagem["count"] / paises.shape[0] * 100).round(2)

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(NETFLIX_DARK)

    # Gradiente vermelho: mais intenso para os países líderes
    r_vals = [max(int(229 - i * 18), 80) for i in range(10)]
    palette = [f"#{rv:02x}{int(9 + i*3):02x}{int(20 + i*3):02x}"
               for i, rv in enumerate(r_vals)]

    sns.barplot(data=contagem, y="country", x="count",
                palette=palette, ax=ax, orient="h")

    for i, (_, row) in enumerate(contagem.iterrows()):
        ax.text(row["count"] + 40, i,
                f'{row["count"]:,}  ({row["pct"]:.1f}%)',
                va="center", ha="left", fontsize=10, color="#dddddd")

    ax.set_title("Top 10 Paises com Mais Conteudo no Catalogo Netflix",
                 fontsize=14, fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Numero de Titulos", fontsize=11)
    ax.set_ylabel("Pais", fontsize=11)
    ax.set_xlim(0, contagem["count"].max() * 1.30)

    plt.tight_layout()
    salvar(fig, "q2_top10_paises.png")
    plt.close(fig)

    print(f"  Lider: {contagem.iloc[0]['country']} ({contagem.iloc[0]['pct']:.1f}%)\n")
    return contagem


# ===========================================================================
# PERGUNTA 3 — Gêneros mais frequentes
# ===========================================================================
def analise_q3(df: pd.DataFrame):
    """
    Explode o campo 'listed_in' e conta os gêneros individuais mais comuns.
    Top 15 gêneros são exibidos em barras horizontais com paleta degradê.

    Decisão analítica: frequência individual em vez de combinações exatas
    para evitar fragmentação excessiva do espaço amostral (há centenas de
    combinações únicas vs. ~40 gêneros distintos).
    """
    print("Q3 - Generos mais frequentes")

    generos = (
        df["listed_in"]
        .str.split(", ")
        .explode()
        .str.strip()
    )

    top_generos = generos.value_counts().head(15).reset_index()
    top_generos.columns = ["genero", "count"]

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(NETFLIX_DARK)

    sns.barplot(data=top_generos, y="genero", x="count",
                palette=sns.color_palette("Reds_r", len(top_generos)),
                ax=ax, orient="h")

    for i, (_, row) in enumerate(top_generos.iterrows()):
        ax.text(row["count"] + 20, i, f'{row["count"]:,}',
                va="center", ha="left", fontsize=9.5, color="#dddddd")

    ax.set_title("Top 15 Generos Mais Frequentes no Catalogo Netflix",
                 fontsize=14, fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Numero de Titulos", fontsize=11)
    ax.set_ylabel("Genero", fontsize=11)
    ax.set_xlim(0, top_generos["count"].max() * 1.2)

    plt.tight_layout()
    salvar(fig, "q3_generos_frequentes.png")
    plt.close(fig)

    print(f"  Genero #1: {top_generos.iloc[0]['genero']} ({top_generos.iloc[0]['count']:,})\n")
    return top_generos


# ===========================================================================
# PERGUNTA 4 — Distribuição das classificações indicativas (rating)
# ===========================================================================
def analise_q4(df: pd.DataFrame):
    """
    Filtra ratings válidos (descarta erros de origem), conta a frequência
    de cada classificação etária e agrupa em faixas de público para
    facilitar a leitura executiva.

    Faixas definidas:
      Adulto | Adolescente | Familia | Infantil | Nao Classificado
    """
    print("Q4 - Distribuicao das classificacoes indicativas")

    validos = ["TV-MA","TV-14","TV-PG","TV-Y","TV-Y7","TV-Y7-FV","TV-G",
               "R","PG-13","PG","G","NC-17","NR","UR"]
    sub = df[df["rating"].isin(validos)].copy()

    contagem = sub["rating"].value_counts().reset_index()
    contagem.columns = ["rating", "count"]

    faixas = {
        "TV-MA": "Adulto",    "R": "Adulto",       "NC-17": "Adulto",
        "TV-14": "Adolescente", "PG-13": "Adolescente",
        "TV-PG": "Familia",   "PG":  "Familia",
        "TV-G":  "Todas Idades", "G": "Todas Idades",
        "TV-Y":  "Infantil",  "TV-Y7": "Infantil",  "TV-Y7-FV": "Infantil",
        "NR":    "Nao Classificado", "UR": "Nao Classificado",
    }
    contagem["faixa"] = contagem["rating"].map(faixas)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor(NETFLIX_DARK)

    # Barras por rating individual
    sns.barplot(data=contagem, x="rating", y="count",
                palette=sns.color_palette("Reds_r", len(contagem)),
                ax=ax1, order=contagem["rating"])
    for bar in ax1.patches:
        h = bar.get_height()
        if h > 0:
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 30,
                     f'{int(h):,}', ha="center", va="bottom",
                     fontsize=8, color="#dddddd")
    ax1.set_title("Volume por Classificacao Indicativa",
                  fontsize=13, fontweight="bold", color="white", pad=10)
    ax1.set_xlabel("Rating", fontsize=10)
    ax1.set_ylabel("Numero de Titulos", fontsize=10)
    ax1.tick_params(axis="x", rotation=40)

    # Pizza por faixa de público
    por_faixa = contagem.groupby("faixa")["count"].sum().sort_values(ascending=False)
    cores_pizza = [NETFLIX_RED, "#b0b0b0", "#ff6b6b", "#666666", "#333333"]
    wedges, texts, autotexts = ax2.pie(
        por_faixa,
        labels=por_faixa.index,
        autopct="%1.1f%%",
        colors=cores_pizza[:len(por_faixa)],
        startangle=140,
        wedgeprops=dict(edgecolor="#141414", linewidth=1.5),
        textprops=dict(color="white", fontsize=10),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
    ax2.set_title("Proporcao por Faixa de Publico",
                  fontsize=13, fontweight="bold", color="white", pad=10)

    plt.tight_layout()
    salvar(fig, "q4_classificacoes_rating.png")
    plt.close(fig)

    adulto_pct = (por_faixa.get("Adulto", 0) / por_faixa.sum() * 100)
    print(f"  Conteudo adulto (TV-MA + R + NC-17): {adulto_pct:.1f}%\n")
    return contagem


# ===========================================================================
# PERGUNTA 5 — Sazonalidade: meses com mais adições de conteúdo
# ===========================================================================
def analise_q5(df: pd.DataFrame):
    """
    Agrupa por mês de adição (1–12) e tipo de conteúdo para revelar
    padrões sazonais na estratégia de lançamentos da Netflix.

    Linhas com área preenchida facilitam a comparação entre formatos
    e permitem identificar picos e vales no calendário editorial.
    """
    print("Q5 - Sazonalidade mensal das adicoes")

    sub = df.dropna(subset=["month_added"]).copy()
    sub["month_added"] = sub["month_added"].astype(int)

    meses_pt = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    sub["mes_nome"] = sub["month_added"].map(meses_pt)

    contagem = (
        sub.groupby(["month_added", "mes_nome", "type"])
        .size()
        .reset_index(name="count")
        .sort_values("month_added")
    )

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor(NETFLIX_DARK)

    cores = {"Movie": NETFLIX_RED, "TV Show": "#cccccc"}

    for tipo, grupo in contagem.groupby("type"):
        grupo = grupo.sort_values("month_added")
        ax.plot(grupo["month_added"], grupo["count"],
                marker="o", linewidth=2.5, markersize=7,
                label=tipo, color=cores.get(tipo, "#aaa"))
        ax.fill_between(grupo["month_added"], grupo["count"],
                        alpha=0.15, color=cores.get(tipo, "#aaa"))

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([meses_pt[m] for m in range(1, 13)], fontsize=10)
    ax.set_title("Sazonalidade Mensal de Adicao de Conteudo Netflix",
                 fontsize=14, fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Mes de Adicao", fontsize=11)
    ax.set_ylabel("Numero de Titulos Adicionados", fontsize=11)
    ax.legend(title="Tipo", framealpha=0.3, facecolor="#222",
              edgecolor="#555", labelcolor="white", title_fontsize=9)

    mes_pico = contagem.groupby("month_added")["count"].sum().idxmax()
    ax.axvline(x=mes_pico, color="#ffcc00", linewidth=1.2,
               linestyle="--", alpha=0.7)
    ax.text(mes_pico + 0.1, ax.get_ylim()[1] * 0.92,
            f"Pico: {meses_pt[mes_pico]}", color="#ffcc00", fontsize=9)

    plt.tight_layout()
    salvar(fig, "q5_sazonalidade_mensal.png")
    plt.close(fig)

    print(f"  Mes de pico: {meses_pt[mes_pico]}\n")
    return contagem


# ===========================================================================
# PERGUNTA 6 — Séries: 1 temporada vs. múltiplas temporadas
# ===========================================================================
def analise_q6(df: pd.DataFrame):
    """
    Filtra apenas TV Shows, extrai o número de temporadas do campo
    'duration' via regex e classifica em categorias.

    Regex '(\d+)' captura o número antes de 'Season(s)'.
    Combinação de pizza (proporção macro) + barras (distribuição detalhada)
    oferece leitura em dois níveis de granularidade.
    """
    print("Q6 - Series: 1 temporada vs. multiplas")

    series = df[df["type"] == "TV Show"].dropna(subset=["duration"]).copy()

    series["n_temporadas"] = (
        series["duration"]
        .str.extract(r"(\d+)")
        .astype(float)
    )
    series = series.dropna(subset=["n_temporadas"])
    series["n_temporadas"] = series["n_temporadas"].astype(int)

    series["categoria"] = series["n_temporadas"].apply(
        lambda x: "1 Temporada" if x == 1 else "Multiplas Temporadas"
    )

    categorias = series["categoria"].value_counts()
    dist_temp  = series["n_temporadas"].value_counts().sort_index().head(12)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor(NETFLIX_DARK)

    # Pizza
    cores_pizza = [NETFLIX_RED, "#888888"]
    wedges, texts, autotexts = ax1.pie(
        categorias,
        labels=categorias.index,
        autopct="%1.1f%%",
        colors=cores_pizza,
        startangle=90,
        wedgeprops=dict(edgecolor="#141414", linewidth=2),
        textprops=dict(color="white", fontsize=11),
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
    ax1.set_title("1 Temporada vs. Multiplas Temporadas",
                  fontsize=13, fontweight="bold", color="white", pad=10)

    # Barras com distribuição exata de temporadas
    sns.barplot(x=dist_temp.index, y=dist_temp.values,
                palette=sns.color_palette("Reds_r", len(dist_temp)),
                ax=ax2)
    ax2.set_title("Distribuicao do Numero de Temporadas",
                  fontsize=13, fontweight="bold", color="white", pad=10)
    ax2.set_xlabel("Numero de Temporadas", fontsize=10)
    ax2.set_ylabel("Quantidade de Series", fontsize=10)
    for bar in ax2.patches:
        h = bar.get_height()
        if h > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, h + 5,
                     f'{int(h):,}', ha="center", va="bottom",
                     fontsize=8.5, color="#dddddd")

    plt.tight_layout()
    salvar(fig, "q6_series_temporadas.png")
    plt.close(fig)

    pct_1 = (categorias.get("1 Temporada", 0) / categorias.sum() * 100)
    print(f"  Series com apenas 1 temporada: {pct_1:.1f}%\n")
    return series


# ===========================================================================
# EXECUÇÃO PRINCIPAL
# ===========================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  ANALISE EXPLORATORIA - CATALOGO NETFLIX")
    print("=" * 60, "\n")

    r1 = analise_q1(df)
    r2 = analise_q2(df)
    r3 = analise_q3(df)
    r4 = analise_q4(df)
    r5 = analise_q5(df)
    r6 = analise_q6(df)

    print("=" * 60)
    print(f"  Analise concluida! Graficos em: ./{OUTPUT_DIR}/")
    print("=" * 60)
