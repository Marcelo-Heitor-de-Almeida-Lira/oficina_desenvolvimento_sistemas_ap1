import streamlit as st
import pandas as pd
import urllib.parse
import requests

API_URL = "http://127.0.0.1:8000"

def avaliar():
    st.set_page_config(
        page_title="Recomendação de Livros",
        layout="wide"
    )

    with st.sidebar:
        if st.button(label="Página Home", key="Home", icon="🏡", width=300):
            st.switch_page("app.py")
        if st.button(label="Avaliar Livros", key="avaliacoes", icon="⭐", width=300):
            st.switch_page("pages/avaliar_livro.py")
        if st.button(label="Recomendações", key="Recomend", icon="🔍", width=300):
            st.switch_page("pages/recomendacoes.py")
    
    st.title("⭐ Avaliar Livro")

    response = requests.get(f"{API_URL}/users_id")
    if response.status_code == 200:
        users_id = response.json()
        users_id = pd.DataFrame(users_id)
        users_id = users_id["user_id"].unique().tolist()
    else:
        st.error("Erro ao buscar ids dos usuários")

    user_id = st.selectbox("Seu ID de usuário", options=users_id)

    response = requests.get(f"{API_URL}/livros_titulo")
    if response.status_code == 200:
        titles = response.json()
        titles = pd.DataFrame(titles)
        titles = titles["title"].tolist()
    else:
        st.error("Erro ao buscar títulos")

    book_title = st.selectbox("Título do livro", options=titles)
    encoded_title = urllib.parse.quote(book_title)

    rating = st.slider("Avaliação", 1, 5, 3)

    if st.button("Enviar Avaliação"):
        response = requests.post(f"{API_URL}/avaliar_livro", params={
            "user_id": user_id,
            "title": book_title,
            "rating": rating
        })
        if response.status_code == 200:
            st.success("Avaliação registrada com sucesso!")
        else:
            st.error("Erro ao salvar avaliação")

def main():
    avaliar()

if __name__ == "__main__":
    main()