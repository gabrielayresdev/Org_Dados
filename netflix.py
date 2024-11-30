import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração inicial do Streamlit
st.set_page_config(page_title="Análise Netflix", layout="wide")

# Título da aplicação
st.title("📊 Análise de Filmes e Séries no Netflix")

# Carregar os dados
@st.cache
def load_data():
    data = pd.read_csv('./netflix_titles.csv')
    return data

data = load_data()

# Exibir os dados brutos
st.subheader("Dados Brutos")
st.write(data.head())

# Remover nulos e lidar com múltiplos países
data['country'] = data['country'].fillna('Desconhecido')
data = data.assign(country=data['country'].str.split(', ')).explode('country')

# Contar o número de shows por país
shows_count = data['country'].value_counts()

# Gráfico: Número de shows por país
st.subheader("🎥 Número de Filmes e Séries por País")
fig, ax = plt.subplots(figsize=(10, 6))
shows_count[:20].plot(kind='barh', color='#db0000', ax=ax)
ax.set_title('Número de Filmes e Séries por País')
ax.set_xlabel('Quantidade de Filmes e Séries')
ax.set_ylabel('Países')
ax.invert_yaxis()
st.pyplot(fig)

# Filtrar por tipo de conteúdo
movies = data[data['type'] == 'Movie']
shows = data[data['type'] == 'TV Show']

# Lidar com múltiplos gêneros
movies = movies.assign(listed_in=movies['listed_in'].str.split(', ')).explode('listed_in')
shows = shows.assign(listed_in=shows['listed_in'].str.split(', ')).explode('listed_in')

# Gêneros de filmes
movie_genres = movies['listed_in'].value_counts()

st.subheader("🎬 Gêneros Mais Populares em Filmes")
fig, ax = plt.subplots(figsize=(10, 6))
movie_genres[:20].plot(kind='barh', color='#db0000', ax=ax)
ax.set_title('Gêneros Mais Populares em Filmes')
ax.set_xlabel('Quantidade de Filmes')
ax.set_ylabel('Gêneros')
ax.invert_yaxis()
st.pyplot(fig)

# Gêneros de séries
show_genres = shows['listed_in'].value_counts()

st.subheader("📺 Gêneros Mais Populares em Séries")
fig, ax = plt.subplots(figsize=(10, 6))
show_genres[:20].plot(kind='barh', color='#db0000', ax=ax)
ax.set_title('Gêneros Mais Populares em Séries')
ax.set_xlabel('Quantidade de Séries')
ax.set_ylabel('Gêneros')
ax.invert_yaxis()
st.pyplot(fig)
