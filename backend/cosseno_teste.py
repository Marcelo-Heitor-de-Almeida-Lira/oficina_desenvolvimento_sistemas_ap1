# TESTE PARA FUNÇÃO DO COSSENO EM DATASETS GRANDES

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from math import sqrt

def load_ratings():
    ratings = pd.read_csv("dataset/ratings.csv", dtype={"user_id": str})

    print("Traansformando dataset in matriz")
    user_item_matrix = ratings.pivot(index="user_id", columns="book_id", values="rating").fillna(0)

    print("Fazendo matriz esparsa")
    sparse_matrix = csr_matrix(user_item_matrix.values)
    return sparse_matrix, user_item_matrix

# Esta funcao se torna obosoleta em frente ao tamanho massivo dos dados (6M)
def cosseno(my_rating, other_rating):
    merged = pd.merge(my_rating, other_rating, on="book_id", suffixes=("_my", "_other"))

    if merged.empty:
        return 0

    xy = (merged["rating_my"] * merged["rating_other"]).sum()
    sum_x2 = (merged["rating_my"] ** 2).sum()
    sum_y2 = (merged["rating_other"] ** 2).sum()

    return xy / (sqrt(sum_x2) * sqrt(sum_y2))
# __________________________________________________________________________________


def ComputeNearestNeighbor(username, user_ratings_matrix, sparse_matrix):
    user_index = user_ratings_matrix.index.get_loc(username)

    print("Calculando similaridade do cosseno")
    similaridades = cosine_similarity(sparse_matrix[user_index], sparse_matrix).flatten()
    
    indices = similaridades.argsort()[::-1]
    
    top_indices = indices[1:6]
    
    return [(user_ratings_matrix.index[i], similaridades[i]) for i in top_indices]


def recomendar(username: str):
    ratings, ratings_matrix = load_ratings()
    print("Dataset carregado")
    
    nearest_neighbor = ComputeNearestNeighbor(username, ratings_matrix, ratings)
    print("Vizihno mais próximo calculado")
    return {"user": username, "nearest": nearest_neighbor}

if __name__ == "__main__":
    recomendacoes = recomendar("Marcelo")
    print(recomendacoes)