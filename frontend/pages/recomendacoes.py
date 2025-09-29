import streamlit as st
import requests
import os
from PIL import Image

API_URL = "http://127.0.0.1:8000"
DEFAULT_COVER = "https://placehold.co/200x300?text=Livro+Nao+Encontrado"

def recomendar():
    st.set_page_config(page_title="Recomendações de Livros", layout="wide")

    with st.sidebar:
        if st.button(label="Página Home", key="Home", icon="🏡", width=300):
            st.switch_page("app.py")
        if st.button(label="Avaliar Livros", key="avaliacoes", icon="⭐", width=300):
            st.switch_page("pages/avaliar_livro.py")
        if st.button(label="Recomendações", key="Recomend", icon="🔍", width=300):
            st.switch_page("pages/recomendacoes.py")
    
    st.title("🔍 Recomendações")
    username = st.text_input("Digite o nome do usuário")

    if st.button("Recomendar"):
        response = requests.get(f"{API_URL}/recomendacao/{username}")
        if response.status_code == 200:
            resultado = response.json()

            # Mostra acurácia
            st.metric("Acurácia", f"{resultado['acuracia']*100:.0f}%")
            st.write(f"Acertos: {resultado['acertos']} de {resultado['total_recomendacoes']} recomendações")

            # Mostra livros
            columns = st.columns(3)
            j = 0
            for book_id in resultado["recommended_books"]:
                col = columns[j % 3]
                response = requests.get(f"{API_URL}/livro/capa_id/{book_id}")
                if response.status_code == 200:
                    livro = response.json()
                    col.write(f"Autor: {livro['author']}")
                    cover_path = livro.get("cover", DEFAULT_COVER)

                    try:
                        if cover_path.startswith("http"):
                            col.image(cover_path, caption=livro["title"], width=300)
                        else:
                            # Se for local
                            if not os.path.exists(cover_path):
                                cover_path = DEFAULT_COVER
                            img = Image.open(cover_path)
                            col.image(img, caption=livro["title"], width=300)
                    except Exception:
                        # Se falhar, usar placeholder
                        col.image(DEFAULT_COVER, caption=livro["title"], width=300)

                else:
                    col.error("Livro não encontrado")
                j += 1
        else:
            st.error("Usuário não encontrado ou erro na API")

def main():
    recomendar()

if __name__ == "__main__":
    main()
