import streamlit as st
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

    user_id = st.text_input("Seu ID de usuário")
    book_title = st.text_input("Título do livro")
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