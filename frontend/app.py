import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

def bar_chart(livro):
    df = pd.DataFrame({
        "Estrelas": ["1⭐", "2⭐", "3⭐", "4⭐", "5⭐"],
        "Quantidade": [
            livro["ratings_1"],
            livro["ratings_2"],
            livro["ratings_3"],
            livro["ratings_4"],
            livro["ratings_5"]
        ]
    })

    fig = px.bar(df, x="Estrelas", y="Quantidade", text="Quantidade",
                 color="Estrelas", title="Distribuição de Avaliações")
    fig.update_traces(textposition="outside")

    return fig

def app():
    st.set_page_config(
        page_title="Recomendação de Livros",
        layout="wide"
    )

    st.title("📚 Sistema de Recomendação de Livros")

    with st.sidebar:
        if st.button(label="Página Home", key="Home", icon="🏡", width=300):
            st.switch_page("app.py")
        if st.button(label="Avaliar Livros", key="avaliacoes", icon="⭐", width=300):
            st.switch_page("pages/avaliar_livro.py")
        if st.button(label="Recomendações", key="Recomend", icon="🔍", width=300):
            st.switch_page("pages/recomendacoes.py")

    st.subheader("📖 Catálogo de livros")

    columns = st.columns(3)

    page = st.session_state.get("page", 1)
    page_size = 15
    
    if st.button("Próxima página"):
        page += 1
        st.session_state.page = page
    

    response = requests.get(f"{API_URL}/livros", params={"page": page, "page_size": page_size})
    if response.status_code == 200:
        livros = response.json()
        books = pd.DataFrame(livros)
        i = 0
        for book_id in books["book_id"]:
            col = columns[i % 3]
            response = requests.get(f"{API_URL}/livro/capa_id/{book_id}")
            if response.status_code == 200:
                livro = response.json()
                col.write(f"Autor: {livro['author']}")
                cover_path = livro["cover"]
                col.image(cover_path, caption=livro["title"], width=300)
            else:
                st.error("Erro ao buscar capa do livro")
            i += 1
    else:
        st.error("Erro ao buscar livros.")
    
    st.subheader("🔍 Buscar livro")

    book_title = st.text_input("Digite o título do livro")

    col1, col2, col3 = st.columns([1,1,2], gap="small")

    if st.button("Buscar livro"):
        response = requests.get(f"{API_URL}/livro/{book_title}")
        if response.status_code == 200:
            livro = response.json()
            if "error" in livro:
                st.warning(livro["error"])
            else:
                response = requests.get(f"{API_URL}/livro/capa_title/{book_title}")
                if response.status_code == 200:
                    cover_path = response.json()
                    col1.image(cover_path, caption=livro["title"], width=200)
                    col2.write(f"ID do livro: {livro["book_id"]}")
                    col2.write(f"Autor(es): {livro["authors"]}")
                    col2.write(f"Ano de publicação: {str(livro["original_publication_year"])}")
                    col2.write(f"Avaliação média: {livro["average_rating"]}")
                    col3.plotly_chart(bar_chart(livro))
                else:
                    st.error("Erro ao buscar capa do livro")
        else:
            st.error("Erro ao buscar livro.")

def main():
    app()

if __name__ == "__main__":
    main()
