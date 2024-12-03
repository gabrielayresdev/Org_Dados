import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import io

# Configuração inicial do Streamlit
st.set_page_config(page_title="Análise Netflix", layout="centered")

# Fonte Netflix
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* Alterar fundo da página */
    .stApp {
        background-color: #141414;
    }

    /* Fonte padrão personalizada */
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #FFFFFF;
        font-size = 20px;
        font-weight: bold;
    }

    /* Classe para título personalizado */
    .custom-title {
        color: #e4101f;  
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }

    /* Classe para subheader personalizado */
    .custom-subheader {
        color: #e4101f;
        font-size: 36px;
        font-weight: bold;
        margin-top: 20px;
    }

    /* Classe para botão */
    .stButton>button {
        background-color: #db0000; 
        color: black; 
        font-size: 20px;
        font-weight: bold;
        border-radius: 5px; 
        padding: 15px 32px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 150px;
        height: 150px;
        display: inline-block;
        margin-right: 10px;
    }
    .stButton>button:hover {
        background-color: #e4101f;
        color: #FFFFFF; 
        font-size: 20px;
        font-weight: bold;
        transform: scale(1.08);
    }
    .stButton>button:active {
        background-color: #a30000;
        transform: scale(1);
        color: #F0F0F0; 
    }
    .button-container {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título da aplicação
st.markdown('<p class="custom-title">📊 Análise de Filmes e Séries no Netflix</p>', unsafe_allow_html=True)

# Carregar os dados
@st.cache_data
def load_data():
    data = pd.read_csv('./netflix_titles.csv')
    return data

data = load_data()

# Exibir os dados brutos
st.markdown('<p class="custom-subheader">Dados Brutos</p>', unsafe_allow_html=True)
st.write(data.head())
st.markdown('<p class = "css">Fonte do Dataset: <a href="https://www.kaggle.com/datasets/spscientist/students-performance-in-exams" target="_blank">Kaggle</a></p>', unsafe_allow_html=True)


# Remover nulos e lidar com múltiplos países
data['country'] = data['country'].fillna('Desconhecido')
data = data.assign(country=data['country'].str.split(', ')).explode('country')

# Contar o número de shows por país
shows_count = data['country'].value_counts()

# Filtrar por tipo de conteúdo
movies = data[data['type'] == 'Movie']
shows = data[data['type'] == 'TV Show']

# Lidar com múltiplos gêneros
movies = movies.assign(listed_in=movies['listed_in'].str.split(', ')).explode('listed_in')
shows = shows.assign(listed_in=shows['listed_in'].str.split(', ')).explode('listed_in')

# Gêneros de filmes e séries
movie_genres = movies['listed_in'].value_counts()
show_genres = shows['listed_in'].value_counts()

def calcular_frequencias(texto):
    frequencias = {}
    for nome in texto.split():
        nome_corrigido = nome.replace("_", " ")  # Restaurar espaços
        frequencias[nome_corrigido] = frequencias.get(nome_corrigido, 0) + 1
    return frequencias

# Removendo nulls e tratando diretores
diretores = data.dropna(subset=['director'])
diretores = diretores.assign(director=diretores['director'].str.split(', ')).explode('director')
diretores.loc[:, "nome_com_underline"] = diretores["director"].str.replace(" ", "_")


# removendo nulls
elenco = data.dropna(subset=['cast'])

elenco = elenco.assign(cast=elenco['cast'].str.split(', ')).explode('cast')

elenco.loc[:, "nome_com_underline"] = elenco["cast"].str.replace(" ", "_")

texto = " ".join(elenco["nome_com_underline"])




# Remover inconsistências
data['date_added'] = data['date_added'].str.strip()

# Converter as strings de Dia Mes, Ano para AAAA-MM-DD
data['date_added'] = pd.to_datetime(data['date_added'], errors='coerce')
data['ano'] = data['date_added'].dt.year.fillna(0).astype(int)

# Pegar dados dos últimos 10 anos
data_dez_anos = data[data['ano'] >= 2011].groupby(['ano', 'type']).size().unstack(fill_value=0)


# Verificar se a coluna 'date_added' possui valores nulos ou de tipo diferente de string
data['date_added'] = data['date_added'].fillna('')

# Converter os valores para string e depois aplicar o método .str.strip()
data['date_added'] = data['date_added'].astype(str).str.strip()

# Converter as strings de Dia-Mês-Ano para formato AAAA-MM-DD
data['date_added'] = pd.to_datetime(data['date_added'], errors='coerce')
data['ano'] = data['date_added'].dt.year.fillna(0).astype(int)

# Filtrar dados para os últimos 10 anos
data_contagem_por_ano = data[data['ano'] >= 2011]
contagem_por_ano = data_contagem_por_ano.groupby('ano').size()


# Definindo as categorias de classificação
classificacao_convertida = {
    'TV-Y': 'Livre', 'TV-Y7': 'Livre', 'TV-G': 'Livre', 'G': 'Livre', 'TV-Y7-FV': 'Livre',
    'PG': '10+', 'TV-PG': '10+',
    'TV-14': '12+', 
    'PG-13': '14+',
    'R': '16+',
    'TV-MA': '18+', 'NC-17': '18+'
}

# Mapear a classificação no DataFrame (substitua 'data' se necessário)
data['rating_category'] = data['rating'].map(classificacao_convertida)

# Tratar valores ausentes (se houver)
data['rating_category'] = data['rating_category'].fillna('Desconhecido')

# Contagem por ano e classificação
classification_counts = data.groupby(['ano', 'rating_category']).size().unstack(fill_value=0)

# Definindo as cores para as classificações
cores_classificacao = {
    'Livre': 'green',
    '10+': 'blue',
    '12+': 'yellow',
    '14+': 'orange',
    '16+': 'red',
    '18+': 'black',
    'Desconhecido': 'gray'
}

# Criar os botões customizados
option = None

# Criar uma caixa para os botões
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)
    with col1:
        if st.button("Número de Filmes e Séries por País"):
            option = "Numero_de_filmes_por_pais"
            
    with col2:
        if st.button("Gêneros de Filmes"):
            option = "Generos_de_filmes"
            
    with col3:
        if st.button("Gêneros de Séries"):
            option = "Generos_de_series"

    with col4:
        if st.button("WordCloud de Diretores"):
            option = "WordCloud_de_diretores"
    
    with col5:
        if st.button("WordCloud de Atores"):
            option = "WordCloud_de_atores"

    with col6:
        if st.button("Filmes vs Séries"):
            option = "filmes_vs_series"

    with col7:
        if st.button("Produções por ano"):
            option = "producoes_por_ano"

    with col8:
        if st.button("Produções por classificação indicativa"):
            option = "producoes_por_classificacao_indicativa"

if option == "Numero_de_filmes_por_pais":
    st.markdown('<p class="custom-subheader">🎬 Número de Filmes e Séries por País</p>', unsafe_allow_html=True)
    
    fig = px.bar(shows_count.head(20), 
                 x=shows_count.head(20).values, 
                 y=shows_count.head(20).index, 
                 orientation='h', 
                 color=shows_count.head(20).values, 
                 color_continuous_scale='reds', 
                 labels={'x': 'Quantidade de Filmes e Séries', 'y': 'Países'}, 
                 title='Número de Filmes e Séries por País')

    fig.update_layout(
        xaxis_title='Quantidade de Filmes e Séries',
        yaxis_title='Países',
        plot_bgcolor='#141414',
        title_x=0.5,
        title_font=dict(size=20, color='#e4101f'),
        paper_bgcolor='#141414',
        font=dict(color='white')
    )

    # Exibir o gráfico interativo no Streamlit
    st.plotly_chart(fig)
    st.markdown('<p class="css">Percebemos no gráfico que os Estados Unidos são dominantes na Netflix, seguido pela Índia. Vemos que o Brasil possui poucos filmes e séries originais.</p>', unsafe_allow_html=True)

elif option == "Generos_de_filmes":
    st.markdown('<p class="custom-subheader">🎥 Gêneros Mais Populares em Filmes</p>', unsafe_allow_html=True)

    genre_df = movie_genres[:20].reset_index()
    genre_df.columns = ['Gênero', 'Quantidade']
    
    fig = px.bar(genre_df, 
                 x='Quantidade', 
                 y='Gênero', 
                 orientation='h',
                 color='Quantidade',
                 color_continuous_scale='reds',
                 labels={'Quantidade': 'Quantidade de Filmes', 'Gênero': 'Gêneros'},
                 title='Gêneros Mais Populares em Filmes')
    fig.update_layout(
        plot_bgcolor='#141414',
        title_x=0.5,
        title_font=dict(size=20, color='#e4101f'),
        paper_bgcolor='#141414',
        font=dict(color='white')
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos nesse gráfico que o foco das séries da Netflix são as internacionais que são feitas para pessoas de todo o globo e de grande orçamento, além disso vimos uma alta em filmes de comédia, ação e aventura, documentários e filmes para a família. Vale destacar também o espaço dado para produções independentes</p>', unsafe_allow_html=True)


elif option == "Generos_de_series":
    st.markdown('<p class="custom-subheader">📺 Gêneros Mais Populares em Séries</p>', unsafe_allow_html=True)
    series_genre_df = show_genres[:20].reset_index()
    series_genre_df.columns = ['Gênero', 'Quantidade']
    
    fig = px.bar(series_genre_df, 
                 x='Quantidade', 
                 y='Gênero', 
                 orientation='h',
                 color='Quantidade',
                 color_continuous_scale='reds',
                 labels={'Quantidade': 'Quantidade de Séries', 'Gênero': 'Gêneros'},
                 title='Gêneros Mais Populares em Séries')
    fig.update_layout(
        plot_bgcolor='#141414',
        title_x=0.5,
        title_font=dict(size=20, color='#e4101f'),
        paper_bgcolor='#141414',
        font=dict(color='white')
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos nesse gráfico que o foco das séries da Netflix são séries internacionais que são feitas para pessoas de todo o globo, além disso vimos programas de comédias em alta, dramas, séries criminais e romances.</p>', unsafe_allow_html=True)


elif option == "WordCloud_de_diretores":
    st.markdown('<p class="custom-subheader">🌐 Nuvem de Palavras dos Diretores</p>', unsafe_allow_html=True)
    wordcloud_diretores = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(calcular_frequencias(" ".join(diretores["nome_com_underline"])))

    image = wordcloud_diretores.to_image()
    img_array = np.array(image)

    fig = px.imshow(img_array)
    fig.update_layout(
        title='Nuvem de Palavras dos Diretores',
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        coloraxis_showscale=False
    )
    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=20, color='#e4101f'),
        paper_bgcolor='#141414',
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos que o fato da Netflix ser uma empresa globalizada os seus produtos contém diretores do mundo todo.</p>', unsafe_allow_html=True)


elif option == "WordCloud_de_atores":
    wordcloud_atores = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(calcular_frequencias(" ".join(elenco["nome_com_underline"])))

    image = wordcloud_atores.to_image()
    img_array = np.array(image)

    fig = px.imshow(img_array)
    fig.update_layout(
        title='Nuvem de Palavras dos Diretores',
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        coloraxis_showscale=False
    )
    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=20, color='#e4101f'),
        paper_bgcolor='#141414',
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos que o fato da Netflix ser uma empresa globalizada os seus produtos contém atores do mundo todo, assim como diretores, destaque para atores indianos, britânicos.</p>', unsafe_allow_html=True)

elif option == "filmes_vs_series":
    st.markdown('<p class="custom-subheader">Filmes vs Séries</p>', unsafe_allow_html=True)
    filmes_series_por_ano = data.groupby(['ano', 'type']).size().reset_index(name='quantidade')

    color_map = {"Movie": "#e4101f", "TV Show": "#ffffff"}

    fig = px.bar(
        filmes_series_por_ano,
        x="ano",
        y="quantidade",
        color="type",
        barmode="group",
        text="quantidade",
        title="Distribuição de Filmes e Séries por Ano",
        labels={"quantidade": "Quantidade", "ano": "Ano", "type": "Tipo"},
        orientation="v",
        color_discrete_map=color_map
    )
    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        legend_title="Tipo",
        template="plotly_dark",
        plot_bgcolor='#141414',
        paper_bgcolor='#141414',
        font=dict(color='white'),
        title_font=dict(size=20, color='#e4101f'),
        title_x=0.5,
        bargap=0.2,
        xaxis=dict(
            range=[2008, 2022],
            tickmode='linear',
            tick0=2008,
            dtick=1,
        ),
        legend=dict(
            title="Tipo",
            font=dict(color="white"),
            bgcolor="#141414",
        )
    )
    fig.update_traces(
        textposition='outside',
        texttemplate='%{text}',
        hoverinfo="x+y+name",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos que a Netflix tem focado na produção e compra de direitos de filmes.</p>', unsafe_allow_html=True)

elif option == "producoes_por_ano":
    st.markdown('<p class="custom-subheader">Produções por Ano</p>', unsafe_allow_html=True)

    producoes_por_ano = data['ano'].value_counts().reset_index()
    producoes_por_ano.columns = ['ano', 'quantidade']
    producoes_por_ano = producoes_por_ano.sort_values(by='ano')

    fig = px.bar(
        producoes_por_ano,
        x="ano",
        y="quantidade",
        title="Quantidade de Produções por Ano",
        labels={"quantidade": "Quantidade", "ano": "Ano"},
        text="quantidade",
    )
    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        template="plotly_dark",
        plot_bgcolor='#141414',
        paper_bgcolor='#141414',
        font=dict(color='white'),
        title_font=dict(size=20, color='#e4101f'),
        title_x=0.5,  # Centraliza o título
        xaxis=dict(
            range=[2008, 2022],
            tickmode='linear',
            tick0=2008,
            dtick=1,
        ),
    )
    fig.update_traces(
        textposition='outside',
        texttemplate='%{text}',
        marker_color='#e4101f',
        marker_line_color='white',
        marker_line_width=1.5,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos que o ano de 2019 foi o ano com maior número de produções da Netflix, vemos também que a pandemia afetou as produções fazendo com que 2021 tenha tido uma produção menor que 2018.</p>', unsafe_allow_html=True)

elif option == "producoes_por_classificacao_indicativa":
    st.markdown('<p class="custom-subheader">Produções por Classificação Indicativa</p>', unsafe_allow_html=True)
    
    classification_counts = classification_counts.reset_index()

    fig = px.bar(
        classification_counts,
        x="ano",
        y=classification_counts.columns[1:],
        title="Produções por Ano e Classificação Indicativa",
        labels={"ano": "Ano", "value": "Quantidade de Produções", "rating_category": "Classificação Indicativa"},
        color_discrete_map=cores_classificacao,
        barmode='stack',
        text_auto=True
    )
    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Quantidade de Produções",
        template="plotly_dark",
        plot_bgcolor='#141414',
        paper_bgcolor='#141414',
        font=dict(color='white'),
        title_font=dict(size=20, color='#e4101f'),
        title_x=0.5,
        legend_title="Classificação Indicativa",
        bargap=0.2,
        xaxis=dict(
            range=[2008, 2022],
            tickmode='linear',
            tick0=2008,
            dtick=1,
        ),
        legend=dict(
            title="Tipo",
            font=dict(color="white"),
            bgcolor="#141414",
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="css">Percebemos que a Netflix tem como foco o público adulto e adolescentes a partir dos doze anos e que o público que menos recebe conteúdo é o infantil.</p>', unsafe_allow_html=True)