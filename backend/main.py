from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from math import sqrt

app = FastAPI()

books = pd.read_csv("dataset/books_clean.csv")

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
    
    top_indices = indices[1:6]
    
    return [(user_ratings_matrix.index[i], similaridades[i]) for i in top_indices]



@app.get("/")
def home():
    return {"message": "API de recomendação funcionando"}

@app.get("/livros")
def get_livros():
    return books.head().to_dict(orient="records")

@app.get("/livro/{id}")
def get_livro(id: int):
    book = books[books["book_id"] == id]

    if book.empty:
        return {"error": "Livro não encontrado"}
    
    return book.iloc[0].to_dict()

@app.get("/recomendacao/{username}")
def recomendar(username: str):
    ratings_df, ratings_matrix, rating_csr = load_ratings_optimized()
    if username not in ratings_df["user_id"].values:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    nearest_neighbor = ComputeNearestNeighbor(username, ratings_matrix, rating_csr)
    return {"user": username, "nearest": nearest_neighbor}
    

@app.post("/avaliar_livro")
def avaliar_livro(user_id: str, book_id: int, rating:int):
    ratings = load_ratings()
    
    new_rating = {'user_id': user_id, 'book_id': book_id, 'rating': rating}
    new_rating_df = pd.DataFrame([new_rating])

    new_ratings = pd.concat([ratings, new_rating_df], ignore_index=True)

    new_ratings.to_csv("dataset/ratings.csv", index=False)