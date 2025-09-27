from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from math import sqrt

app = FastAPI()

books = pd.read_csv("dataset/books_clean.csv")
covers = pd.read_csv("covers.csv")

DEFAULT_COVER = "https://placehold.co/200x300?text=Livro+Nao+Encontrado"

def load_ratings():
    ratings = pd.read_csv("dataset/ratings.csv", dtype={"user_id": str})
    return ratings

def load_ratings_optimized():
    ratings = pd.read_csv("dataset/ratings.csv", dtype={"user_id": str})

    user_item_matrix = ratings.pivot(index="user_id", columns="book_id", values="rating").fillna(0)

    sparse_matrix = csr_matrix(user_item_matrix.values)
    return ratings, user_item_matrix, sparse_matrix

# Esta função se tornou obsoleta por causa do tamanho massivo dos dados
def cosseno(my_rating, other_rating):
    merged = pd.merge(my_rating, other_rating, on="book_id", suffixes=("_my", "_other"))

    if merged.empty:
        return 0

    xy = (merged["rating_my"] * merged["rating_other"]).sum()
    sum_x2 = (merged["rating_my"] ** 2).sum()
    sum_y2 = (merged["rating_other"] ** 2).sum()

    return xy / (sqrt(sum_x2) * sqrt(sum_y2))



def ComputeNearestNeighbor(username, user_ratings_matrix, sparse_matrix):
    user_index = user_ratings_matrix.index.get_loc(username)

    print("Calculando similaridade do cosseno")
    similaridades = cosine_similarity(sparse_matrix[user_index], sparse_matrix).flatten()
    
    indices = similaridades.argsort()[::-1]

    nearest_neighbor = indices[1]
    
    return str(user_ratings_matrix.index[nearest_neighbor])


def get_books_from_user(user_id):
    ratings = load_ratings()

    user_ratings = ratings[ratings["user_id"] == user_id]

    user_books = user_ratings["book_id"].values.tolist()

    return user_books



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
    cover_path = cover["cover_path"].values[0]
    if not pd.notna(cover_path) or cover_path.strip() == "":
        cover_path = DEFAULT_COVER
    return cover_path

@app.get("/livro/capa_id/{id}")
def get_capa(id: int):
    cover = covers[covers["book_id"] == id]
    cover_path = cover["cover_path"].values[0]
    title = cover["title"].values[0]
    author = cover["author"].values[0]
    if not pd.notna(cover_path) or cover_path.strip() == "":
        cover_path = DEFAULT_COVER
    return {"cover": cover_path, "title": title, "author": author}

@app.get("/recomendacao/{username}")
def recomendar(username: str):
    ratings_df, ratings_matrix, rating_csr = load_ratings_optimized()
    if username not in ratings_df["user_id"].values:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    nearest_neighbor = ComputeNearestNeighbor(username, ratings_matrix, rating_csr)

    recomended_books = get_books_from_user(nearest_neighbor)

    return recomended_books
    

@app.post("/avaliar_livro")
def avaliar_livro(user_id: str, title: str, rating:int):
    ratings = load_ratings()

    book = books[books["title"] == title]

    book_id = book["book_id"].values[0]
    
    new_rating = {'user_id': user_id, 'book_id': book_id, 'rating': rating}
    new_rating_df = pd.DataFrame([new_rating])

    new_ratings = pd.concat([ratings, new_rating_df], ignore_index=True)

    new_ratings.to_csv("dataset/ratings.csv", index=False)