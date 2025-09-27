import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def recomendar():
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

    st.title("Recomendações")

    username = st.text_input("Digite o nome do usuário")
    if st.button("Recomendar"):
        response = requests.get(f"{API_URL}/recomendacao/{username}")
        if response.status_code == 200:
            resultado = response.json()
            st.write(f"Usuário base: {username}")
            columns = st.columns(3)
            j=0
            for book in resultado:
                col = columns[j % 3]
                response = requests.get(f"{API_URL}/livro/capa_id/{book}")
                if response.status_code == 200:
                    livro = response.json()
                    col.write(f"Autor: {livro['author']}")
                    col.image(livro["cover"], caption=livro["title"], width=300)
                else:
                    st.error("Livro não encontrado")
                j += 1
        else:
            st.error("Usuário não encontrado ou erro na API")

def main():
    recomendar()

if __name__ == "__main__":
    main()