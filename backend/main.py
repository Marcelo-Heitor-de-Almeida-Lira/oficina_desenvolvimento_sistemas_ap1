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
    ratings = pd.read_csv("dataset/ratings_reduced.csv", dtype={"user_id": str})
    return ratings

def load_ratings_optimized():
    ratings = pd.read_csv("dataset/ratings_reduced.csv", dtype={"user_id": str})
    user_item_matrix = ratings.pivot(index="user_id", columns="book_id", values="rating").fillna(0)
    sparse_matrix = csr_matrix(user_item_matrix.values)
    return ratings, user_item_matrix, sparse_matrix

def ComputeNearestNeighbor(username, user_ratings_matrix, sparse_matrix):
    user_index = user_ratings_matrix.index.get_loc(username)

    similaridades = cosine_similarity(sparse_matrix[user_index], sparse_matrix).flatten()

    indices = similaridades.argsort()[::-1]

    neighbors = []

    for idx in indices[1:10]:
        neighbors.append({
            "username": str(user_ratings_matrix.index[idx]),
            "cosine": float(similaridades[idx])
        })

    return neighbors

def get_recommendation_from_users(neighbors):
    ratings = load_ratings()

    books_recommend = set()
    influences = {}
    total_similarity = 0
    book_points = {}

    for user in neighbors:
        user_rating = ratings[ratings["user_id"] == user["username"]]
        for book in user_rating["book_id"]:
            books_recommend.add(book)
        total_similarity += user["cosine"]

    for user in neighbors:
        influences[user["username"]] = user["cosine"] / total_similarity
    
    for book in books_recommend:
        book_points_neighbors = 0
        for user in neighbors:
            user_rating = ratings[ratings["user_id"] == user["username"]]
            user_book = user_rating[user_rating["book_id"] == book]
            if not user_book.empty:
                user_book_rating = user_book["rating"].values[0]
            else:
                user_book_rating = 0
            user_cosine = influences[user["username"]]
            book_points_neighbors += user_book_rating * user_cosine
        book_points[book] = book_points_neighbors

    top_books = dict(
        sorted(book_points.items(), key=lambda x: x[1], reverse=True)[:21]
    )

    return top_books

# --- Rotas ---

@app.get("/")
def home():
    return {"message": "API de recomendação funcionando"}

@app.get("/livros_titulo")
def get_title_books():
    return books.fillna("").to_dict(orient="records")

@app.get("/users_id")
def get_users_id():
    ratings = load_ratings()
    return ratings.to_dict(orient="records")

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
    nearest_neighbors = ComputeNearestNeighbor(username, user_item_matrix, sparse_matrix)
    recomended_books = get_recommendation_from_users(nearest_neighbors)

    # Calcular acurácia
    test_books = set(test_ratings["book_id"].values.tolist())
    acertos = len(test_books & recomended_books.keys())
    acuracia = acertos / len(recomended_books) if recomended_books else 0
    acuracia_teste = acertos / len(test_books)

    return {
        "recommended_books": list(recomended_books.keys()),
        "test_books": test_books,
        "total_teste": len(test_books),
        "acertos": acertos,
        "total_recomendacoes": len(recomended_books),
        "acuracia": round(acuracia, 2),
        "acuracia_teste": round(acuracia_teste, 2)
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
