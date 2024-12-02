import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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
        color: #e4101f;
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
    }
    .stButton>button:active {
        background-color: #a30000;
        transform: scale(0.98);
        color: #F0F0F0; 
    }
    .stButton>button.pressed {
        background-color: #a30000;
        transform: scale(0.98);
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

# Removendo nulls e tratando diretores
diretores = data.dropna(subset=['director'])
diretores = diretores.assign(director=diretores['director'].str.split(', ')).explode('director')
diretores.loc[:, "nome_com_underline"] = diretores["director"].str.replace(" ", "_")

# Contando a frequência dos nomes
texto = " ".join(diretores["nome_com_underline"])
frequencias = {}
for nome in texto.split():
    nome_corrigido = nome.replace("_", " ")  # Restaurar espaços
    frequencias[nome_corrigido] = frequencias.get(nome_corrigido, 0) + 1


# removendo nulls
elenco = data.dropna(subset=['cast'])

elenco = elenco.assign(cast=elenco['cast'].str.split(', ')).explode('cast')

elenco.loc[:, "nome_com_underline"] = elenco["cast"].str.replace(" ", "_")

texto = " ".join(elenco["nome_com_underline"])

frequencias = {}
for nome in texto.split():
    nome_corrigido = nome.replace("_", " ")  # Restaurar espaços
    frequencias[nome_corrigido] = frequencias.get(nome_corrigido, 0) + 1


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

# Mapear a classificação no DataFrame
data['rating_category'] = data['rating'].map(classificacao_convertida)

# Filtrando os dados dos últimos anos
df_ultimos_anos = data[data['ano'] >= 2011]

# Contagem por ano e classificação
classification_counts = df_ultimos_anos.groupby(['ano', 'rating_category']).size().unstack(fill_value=0)

# Definindo as cores para as classificações
cores_classificacao = {
    'Livre': 'green',
    '10+': 'blue',
    '12+': 'yellow',
    '14+': 'orange',
    '16+': 'red',
    '18+': 'black'
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

# Exibir o gráfico conforme a opção do usuário
if option == "Numero_de_filmes_por_pais":
    st.markdown('<p class="custom-subheader">🎬 Gêneros Mais Populares em Filmes</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    shows_count[:20].plot(kind='barh', color='#db0000', ax=ax)
    ax.set_title('Número de Filmes e Séries por País')
    ax.set_xlabel('Quantidade de Filmes e Séries')
    ax.set_ylabel('Países')
    ax.invert_yaxis()
    st.pyplot(fig)

elif option == "Generos_de_filmes":
    st.markdown('<p class="custom-subheader">🎬 Gêneros Mais Populares em Filmes</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    movie_genres[:20].plot(kind='barh', color='#db0000', ax=ax)
    ax.set_title('Gêneros Mais Populares em Filmes')
    ax.set_xlabel('Quantidade de Filmes')
    ax.set_ylabel('Gêneros')
    ax.invert_yaxis()
    st.pyplot(fig)

elif option == "Generos_de_series":
    st.markdown('<p class="custom-subheader">📺 Gêneros Mais Populares em Séries</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    show_genres[:20].plot(kind='barh', color='#db0000', ax=ax)
    ax.set_title('Gêneros Mais Populares em Séries')
    ax.set_xlabel('Quantidade de Séries')
    ax.set_ylabel('Gêneros')
    ax.invert_yaxis()
    st.pyplot(fig)

elif option == "WordCloud_de_diretores":
    # Gerando a WordCloud
    wordcloud_diretores = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(frequencias)
    # Exibindo a WordCloud
    st.markdown('<p class="custom-subheader">🌐 Nuvem de Palavras dos Diretores</p>', unsafe_allow_html=True)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud_diretores, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

elif option == "WordCloud_de_atores":
    # Foi preciso criar com base na frequêcia, caso contrário, nome e sobrenome seriam considerados palavras diferentes
    wordcloud_atores = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(frequencias)

    st.markdown('<p class="custom-subheader">🙎‍♂️ Nuvem de Palavras dos Atores</p>', unsafe_allow_html=True)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud_atores, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    st.pyplot(plt)

elif option == "filmes_vs_series":
    st.markdown('<p class="custom-subheader">Filmes vs Séries</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))  # Criar uma figura para o gráfico
    ax = data_dez_anos.plot(kind='bar', ax=ax, width=0.8, color=['black', '#db0000'])
    ax.set_title('Produções por Ano (Filmes vs Séries)', fontsize=14)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Quantidade de Produções', fontsize=12)
    ax.set_xticklabels(data_dez_anos.index, rotation=45)
    ax.legend(title='Tipo de Produção', title_fontsize='13', labels=['Filmes', 'Séries'], fontsize='11', 
              frameon=True, loc='upper left', facecolor='lightgray', edgecolor='black')

    st.pyplot(fig)

elif option == "producoes_por_ano":
    st.markdown('<p class="custom-subheader">Produções por ano</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(contagem_por_ano.index, contagem_por_ano, color='#db0000')
    ax.set_title('Número de Produções por Ano', fontsize=14)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Número de Produções', fontsize=12)
    ax.set_xticklabels(contagem_por_ano.index, rotation=45)

    plt.tight_layout()
    st.pyplot(fig)

elif option == "producoes_por_classificacao_indicativa":
    st.markdown('<p class="custom-subheader">Produções por Classificação Indicativa</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    classification_counts.plot(kind='bar', stacked=False, ax=ax, width=0.8,
                               color=[cores_classificacao.get(x, 'gray') for x in classification_counts.columns])
    ax.set_title('Produções por Ano e Classificação Indicativa', fontsize=14)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Quantidade de Produções', fontsize=12)
    ax.set_xticklabels(classification_counts.index, rotation=45)
    ax.legend(title="Classificação Indicativa", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

    plt.tight_layout()
    st.pyplot(fig)