from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from math import sqrt

app = FastAPI()

# Carregamento de dados
books = pd.read_csv("dataset/books_clean.csv")
covers = pd.read_csv("covers.csv")

DEFAULT_COVER = "https://placehold.co/200x300?text=Livro+Nao+Encontrado"

# --- Funções auxiliares ---

def load_ratings():
    ratings = pd.read_csv("dataset/ratings.csv", dtype={"user_id": str})
    return ratings

def load_ratings_optimized():
    ratings = pd.read_csv("dataset/ratings.csv", dtype={"user_id": str})
    user_item_matrix = ratings.pivot(index="user_id", columns="book_id", values="rating").fillna(0)
    sparse_matrix = csr_matrix(user_item_matrix.values)
    return ratings, user_item_matrix, sparse_matrix

def ComputeNearestNeighbor(username, user_ratings_matrix, sparse_matrix):
    user_index = user_ratings_matrix.index.get_loc(username)
    similaridades = cosine_similarity(sparse_matrix[user_index], sparse_matrix).flatten()
    indices = similaridades.argsort()[::-1]
    nearest_neighbor = indices[1]  # pega o segundo, pois o primeiro é ele mesmo
    return str(user_ratings_matrix.index[nearest_neighbor])

def get_books_from_user(user_id):
    ratings = load_ratings()
    user_ratings = ratings[ratings["user_id"] == user_id]
    user_books = user_ratings["book_id"].values.tolist()
    return user_books

# --- Rotas ---

@app.get("/")
def home():
    return {"message": "API de recomendação funcionando"}

@app.get("/livros")
def get_livros(page: int = 1, page_size: int = 15):
    start = (page - 1) * page_size
    end = start + page_size
    page_books = books.iloc[start:end]
    return page_books.to_dict(orient="records")

@app.get("/livro/{title}")
def get_livro(title: str):
    book = books[books["title"] == title]
    if book.empty:
        return {"error": "Livro não encontrado"}
    return book.iloc[0].to_dict()

@app.get("/livro/capa_title/{title}")
def get_capa(title: str):
    cover = covers[covers["title"] == title]
    cover_path = cover["cover_path"].values[0] if not cover.empty else DEFAULT_COVER
    if not pd.notna(cover_path) or cover_path.strip() == "":
        cover_path = DEFAULT_COVER
    return cover_path

@app.get("/livro/capa_id/{id}")
def get_capa(id: int):
    cover = covers[covers["book_id"] == id]
    if cover.empty:
        return {"cover": DEFAULT_COVER, "title": "Desconhecido", "author": "Desconhecido"}
    cover_path = cover["cover_path"].values[0]
    title = cover["title"].values[0]
    author = cover["author"].values[0]
    if not pd.notna(cover_path) or cover_path.strip() == "":
        cover_path = DEFAULT_COVER
    return {"cover": cover_path, "title": title, "author": author}

# --- Recomendação com acurácia ---
@app.get("/recomendacao/{username}")
def recomendar(username: str, test_ratio: float = Query(0.2, ge=0.1, le=0.9)):
    ratings_df, ratings_matrix, rating_csr = load_ratings_optimized()
    if username not in ratings_df["user_id"].values:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user_ratings_all = ratings_df[ratings_df["user_id"] == username]
    if len(user_ratings_all) < 2:
        raise HTTPException(status_code=400, detail="Usuário precisa ter mais de 1 avaliação para cálculo de acurácia")

    # Shuffle e split treino/teste
    user_ratings_shuffled = user_ratings_all.sample(frac=1, random_state=42)
    split_index = int(len(user_ratings_shuffled) * (1 - test_ratio))
    train_ratings = user_ratings_shuffled.iloc[:split_index]
    test_ratings = user_ratings_shuffled.iloc[split_index:]

    # Criar ratings de treino removendo os itens de teste do usuário
    ratings_train = ratings_df.copy()
    ratings_train = ratings_train[
        ~((ratings_train["user_id"] == username) &
          (ratings_train["book_id"].isin(test_ratings["book_id"])))
    ]

    # Matriz de treino
    user_item_matrix = ratings_train.pivot(index="user_id", columns="book_id", values="rating").fillna(0)
    sparse_matrix = csr_matrix(user_item_matrix.values)

    # Vizinho mais próximo
    nearest_neighbor = ComputeNearestNeighbor(username, user_item_matrix, sparse_matrix)
    recomended_books = get_books_from_user(nearest_neighbor)

    # Calcular acurácia
    test_books = set(test_ratings["book_id"].values.tolist())
    recommended_books_set = set(recomended_books)
    acertos = len(test_books & recommended_books_set)
    acuracia = acertos / len(recomended_books) if recomended_books else 0

    return {
        "recommended_books": recomended_books,
        "acertos": acertos,
        "total_recomendacoes": len(recomended_books),
        "acuracia": round(acuracia, 2)
    }

# --- Avaliar livro ---
@app.post("/avaliar_livro")
def avaliar_livro(user_id: str, title: str, rating: int):
    ratings = load_ratings()
    book = books[books["title"] == title]
    if book.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    book_id = book["book_id"].values[0]
    new_rating = {'user_id': user_id, 'book_id': book_id, 'rating': rating}
    new_ratings_df = pd.DataFrame([new_rating])
    new_ratings = pd.concat([ratings, new_ratings_df], ignore_index=True)
    new_ratings.to_csv("dataset/ratings.csv", index=False)
    return {"message": "Avaliação registrada com sucesso"}
