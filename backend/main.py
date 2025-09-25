from fastapi import FastAPI
import pandas as pd

app = FastAPI()

books = pd.read_csv("dataset/books_clean.csv")

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

@app.post("/avaliar_livro")
def avaliar_livro(user_id: str, book_id: int, rating:int):
    ratings = pd.read_csv("dataset/ratings.csv")
    
    new_rating = {'user_id': user_id, 'book_id': book_id, 'rating': rating}
    new_rating_df = pd.DataFrame([new_rating])

    new_ratings = pd.concat([ratings, new_rating_df], ignore_index=True)

    new_ratings.to_csv("dataset/ratings.csv", index=False)