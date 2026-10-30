"""
Análise exploratória do catálogo da Netflix.

Responde 6 perguntas sobre o dataset netflix_titles.csv (Kaggle) e salva um
gráfico por pergunta na pasta graficos/.

Uso:
    python analise_netflix.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # salva os gráficos em arquivo, sem abrir janela

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

ARQUIVO_DADOS = "netflix_titles.csv"
PASTA_GRAFICOS = "graficos"

VERMELHO = "#E50914"
FUNDO = "#141414"

MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

sns.set_theme(
    style="darkgrid",
    rc={
        "figure.facecolor": FUNDO,
        "axes.facecolor": "#1e1e1e",
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#e0e0e0",
        "xtick.color": "#cccccc",
        "ytick.color": "#cccccc",
        "grid.color": "#2a2a2a",
        "grid.linewidth": 0.6,
        "text.color": "#e0e0e0",
        "font.family": "DejaVu Sans",
    },
)


def carregar_dados(caminho: str) -> pd.DataFrame:
    """Lê o CSV, converte a data de adição e remove as linhas com rating inválido."""
    df = pd.read_csv(caminho)

    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    # Em 3 linhas a duração ("74 min") foi gravada na coluna rating por engano
    rating_errado = df["rating"].str.contains(r"\d+ min", na=False)
    return df[~rating_errado].copy()


def salvar(fig: plt.Figure, nome: str) -> None:
    caminho = os.path.join(PASTA_GRAFICOS, nome)
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Gráfico salvo em {caminho}")


def estilizar_legenda(ax: plt.Axes) -> None:
    ax.legend(title="Tipo", framealpha=0.3, facecolor="#222",
              edgecolor="#555", labelcolor="white", title_fontsize=9)


def separar_valores(coluna: pd.Series) -> pd.Series:
    """Transforma 'A, B, C' em uma linha por valor (países, gêneros etc.)."""
    return coluna.dropna().str.split(",").explode().str.strip().loc[lambda s: s != ""]


def q1_filmes_vs_series(df: pd.DataFrame) -> None:
    """Como a divisão entre filmes e séries evoluiu ao longo dos anos?"""
    print("1. Filmes vs. séries por ano")

    por_ano = (
        df.dropna(subset=["year_added"])
        .groupby(["year_added", "type"]).size()
        .unstack(fill_value=0)
    )
    por_ano.index = por_ano.index.astype(int)
    percentual = por_ano.div(por_ano.sum(axis=1), axis=0) * 100

    anos = por_ano.index.tolist()
    cores = {"Movie": VERMELHO, "TV Show": "#aaaaaa"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), gridspec_kw={"hspace": 0.45})

    # Em cima, a proporção de cada tipo; embaixo, o volume absoluto
    base = np.zeros(len(anos))
    for tipo in percentual.columns:
        ax1.fill_between(anos, base, base + percentual[tipo], color=cores[tipo],
                         alpha=0.85, label=tipo)
        base += percentual[tipo].values
    ax1.set_ylim(0, 100)
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax1.set_ylabel("Participação (%)", fontsize=11)
    ax1.set_title("Filmes vs. séries: proporção por ano", fontsize=13,
                  fontweight="bold", color="white", pad=10)
    ax1.set_xticks(anos)
    ax1.tick_params(axis="x", rotation=45)
    estilizar_legenda(ax1)

    x = np.arange(len(anos))
    largura = 0.35
    for i, tipo in enumerate(por_ano.columns):
        deslocamento = (i - (len(por_ano.columns) - 1) / 2) * largura
        ax2.bar(x + deslocamento, por_ano[tipo], width=largura, label=tipo,
                color=cores[tipo], alpha=0.9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(anos, rotation=45, ha="right")
    ax2.set_ylabel("Títulos adicionados", fontsize=11)
    ax2.set_xlabel("Ano de adição à plataforma", fontsize=11)
    ax2.set_title("Títulos adicionados por ano", fontsize=13,
                  fontweight="bold", color="white", pad=10)
    estilizar_legenda(ax2)

    salvar(fig, "q1_evolucao_filmes_series.png")

    pico = por_ano.sum(axis=1).idxmax()
    ultimo = anos[-1]
    print(f"  Ano com mais adições: {pico} ({por_ano.loc[pico].sum():,} títulos)")
    print(f"  {ultimo}: filmes {percentual.loc[ultimo, 'Movie']:.1f}% | "
          f"séries {percentual.loc[ultimo, 'TV Show']:.1f}%\n")


def q2_top10_paises(df: pd.DataFrame) -> None:
    """Quais são os 10 países com mais títulos no catálogo?"""
    print("2. Top 10 países")

    # Coproduções contam uma vez para cada país envolvido
    paises = separar_valores(df["country"])
    top10 = paises.value_counts().head(10).rename_axis("pais").reset_index(name="titulos")
    top10["pct"] = top10["titulos"] / len(paises) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=top10, y="pais", x="titulos", hue="pais", legend=False,
                palette=sns.color_palette("Reds_r", len(top10)), ax=ax, orient="h")
    for i, linha in top10.iterrows():
        ax.text(linha["titulos"] + 40, i, f'{linha["titulos"]:,}  ({linha["pct"]:.1f}%)',
                va="center", ha="left", fontsize=10, color="#dddddd")
    ax.set_title("Top 10 países com mais títulos no catálogo", fontsize=14,
                 fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Número de títulos", fontsize=11)
    ax.set_ylabel("País", fontsize=11)
    ax.set_xlim(0, top10["titulos"].max() * 1.30)

    salvar(fig, "q2_top10_paises.png")
    print(f"  Líder: {top10.iloc[0]['pais']} ({top10.iloc[0]['pct']:.1f}% das menções de país)\n")


def q3_generos(df: pd.DataFrame) -> None:
    """Quais gêneros aparecem mais?"""
    print("3. Gêneros mais frequentes")

    # Cada título pode ter vários gêneros: conta cada gênero separadamente
    top15 = (separar_valores(df["listed_in"]).value_counts().head(15)
             .rename_axis("genero").reset_index(name="titulos"))

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=top15, y="genero", x="titulos", hue="genero", legend=False,
                palette=sns.color_palette("Reds_r", len(top15)), ax=ax, orient="h")
    for i, linha in top15.iterrows():
        ax.text(linha["titulos"] + 20, i, f'{linha["titulos"]:,}',
                va="center", ha="left", fontsize=9.5, color="#dddddd")
    ax.set_title("Top 15 gêneros do catálogo", fontsize=14,
                 fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Número de títulos", fontsize=11)
    ax.set_ylabel("Gênero", fontsize=11)
    ax.set_xlim(0, top15["titulos"].max() * 1.2)

    salvar(fig, "q3_generos_frequentes.png")
    print(f"  Gênero nº 1: {top15.iloc[0]['genero']} ({top15.iloc[0]['titulos']:,})\n")


def q4_classificacao(df: pd.DataFrame) -> None:
    """Como o catálogo se divide por classificação indicativa?"""
    print("4. Classificação indicativa")

    faixas = {
        "TV-MA": "Adulto", "R": "Adulto", "NC-17": "Adulto",
        "TV-14": "Adolescente", "PG-13": "Adolescente",
        "TV-PG": "Família", "PG": "Família",
        "TV-G": "Todas as idades", "G": "Todas as idades",
        "TV-Y": "Infantil", "TV-Y7": "Infantil", "TV-Y7-FV": "Infantil",
        "NR": "Não classificado", "UR": "Não classificado",
    }
    contagem = (df.loc[df["rating"].isin(faixas), "rating"].value_counts()
                .rename_axis("rating").reset_index(name="titulos"))
    por_faixa = (contagem.groupby(contagem["rating"].map(faixas))["titulos"].sum()
                 .sort_values(ascending=False))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    sns.barplot(data=contagem, x="rating", y="titulos", hue="rating", legend=False,
                palette=sns.color_palette("Reds_r", len(contagem)), ax=ax1)
    for barra in ax1.patches:
        altura = barra.get_height()
        ax1.text(barra.get_x() + barra.get_width() / 2, altura + 30, f"{int(altura):,}",
                 ha="center", va="bottom", fontsize=8, color="#dddddd")
    ax1.set_title("Títulos por classificação", fontsize=13,
                  fontweight="bold", color="white", pad=10)
    ax1.set_xlabel("Classificação", fontsize=10)
    ax1.set_ylabel("Número de títulos", fontsize=10)
    ax1.tick_params(axis="x", rotation=40)

    _, _, percentuais = ax2.pie(
        por_faixa, labels=por_faixa.index, autopct="%1.1f%%", startangle=140,
        colors=[VERMELHO, "#b0b0b0", "#ff6b6b", "#666666", "#333333", "#999999"][:len(por_faixa)],
        wedgeprops={"edgecolor": FUNDO, "linewidth": 1.5},
        textprops={"color": "white", "fontsize": 10},
    )
    for texto in percentuais:
        texto.set_fontsize(9)
    ax2.set_title("Proporção por faixa de público", fontsize=13,
                  fontweight="bold", color="white", pad=10)

    salvar(fig, "q4_classificacoes_rating.png")
    adulto = por_faixa.get("Adulto", 0) / por_faixa.sum() * 100
    print(f"  Conteúdo adulto (TV-MA, R, NC-17): {adulto:.1f}%\n")


def q5_sazonalidade(df: pd.DataFrame) -> None:
    """Em quais meses entram mais títulos?"""
    print("5. Sazonalidade mensal")

    por_mes = (df.dropna(subset=["month_added"])
               .groupby([df["month_added"].astype("Int64"), "type"]).size()
               .unstack(fill_value=0))

    fig, ax = plt.subplots(figsize=(13, 6))
    cores = {"Movie": VERMELHO, "TV Show": "#cccccc"}
    for tipo in por_mes.columns:
        ax.plot(por_mes.index, por_mes[tipo], marker="o", linewidth=2.5,
                markersize=7, label=tipo, color=cores[tipo])
        ax.fill_between(por_mes.index, por_mes[tipo], alpha=0.15, color=cores[tipo])

    total = por_mes.sum(axis=1)
    pico, vale = int(total.idxmax()), int(total.idxmin())
    ax.axvline(x=pico, color="#ffcc00", linewidth=1.2, linestyle="--", alpha=0.7)
    ax.text(pico + 0.1, ax.get_ylim()[1] * 0.92, f"Pico: {MESES[pico]}",
            color="#ffcc00", fontsize=9)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES.values(), fontsize=10)
    ax.set_title("Títulos adicionados por mês do ano", fontsize=14,
                 fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Mês de adição", fontsize=11)
    ax.set_ylabel("Títulos adicionados", fontsize=11)
    estilizar_legenda(ax)

    salvar(fig, "q5_sazonalidade_mensal.png")
    print(f"  Mês com mais adições: {MESES[pico]} ({total[pico]:,}) | "
          f"com menos: {MESES[vale]} ({total[vale]:,})\n")


def q6_temporadas(df: pd.DataFrame) -> None:
    """Quantas séries têm só 1 temporada?"""
    print("6. Séries: 1 temporada vs. várias")

    series = df[df["type"] == "TV Show"].copy()
    # duration vem como "1 Season" ou "3 Seasons": pega só o número
    series["temporadas"] = series["duration"].str.extract(r"(\d+)").astype(float)
    series = series.dropna(subset=["temporadas"])
    series["temporadas"] = series["temporadas"].astype(int)

    categorias = (series["temporadas"].eq(1)
                  .map({True: "1 temporada", False: "2 ou mais temporadas"})
                  .value_counts())
    distribuicao = series["temporadas"].value_counts().sort_index().head(12)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    _, _, percentuais = ax1.pie(
        categorias, labels=categorias.index, autopct="%1.1f%%", startangle=90,
        colors=[VERMELHO, "#888888"],
        wedgeprops={"edgecolor": FUNDO, "linewidth": 2},
        textprops={"color": "white", "fontsize": 11},
    )
    for texto in percentuais:
        texto.set_fontsize(11)
        texto.set_fontweight("bold")
    ax1.set_title("1 temporada vs. 2 ou mais", fontsize=13,
                  fontweight="bold", color="white", pad=10)

    sns.barplot(x=distribuicao.index, y=distribuicao.values, hue=distribuicao.index,
                legend=False, palette=sns.color_palette("Reds_r", len(distribuicao)), ax=ax2)
    for barra in ax2.patches:
        altura = barra.get_height()
        ax2.text(barra.get_x() + barra.get_width() / 2, altura + 5, f"{int(altura):,}",
                 ha="center", va="bottom", fontsize=8.5, color="#dddddd")
    ax2.set_title("Séries por número de temporadas", fontsize=13,
                  fontweight="bold", color="white", pad=10)
    ax2.set_xlabel("Temporadas", fontsize=10)
    ax2.set_ylabel("Séries", fontsize=10)

    salvar(fig, "q6_series_temporadas.png")
    pct = categorias["1 temporada"] / categorias.sum() * 100
    print(f"  Séries com 1 temporada: {pct:.1f}%\n")


def main() -> None:
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    df = carregar_dados(ARQUIVO_DADOS)
    print(f"Dataset: {len(df):,} títulos | adicionados entre "
          f"{int(df['year_added'].min())} e {int(df['year_added'].max())}\n")

    q1_filmes_vs_series(df)
    q2_top10_paises(df)
    q3_generos(df)
    q4_classificacao(df)
    q5_sazonalidade(df)
    q6_temporadas(df)

    print(f"Pronto! Gráficos em {PASTA_GRAFICOS}/")


if __name__ == "__main__":
    main()
