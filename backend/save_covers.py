# Código para pegar as capas dos livros por uma
# API e salvá-las em 'covers.csv'

import os
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cria pasta para salvar capas
os.makedirs("book_covers", exist_ok=True)

# --- Funções auxiliares ---
def get_googlebooks_cover(isbn=None, title=None, author=None):
    try:
        if isbn:
            query = f"isbn:{isbn}"
        else:
            query = f"intitle:{title}+inauthor:{author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            return res["items"][0]["volumeInfo"].get("imageLinks", {}).get("thumbnail")
    except:
        return None
    return None

def download_and_resize(url, filename, size=(200,300)):
    """Baixa e redimensiona uma imagem para pasta book_covers/"""
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = img.resize(size)
            path = os.path.join("book_covers", filename)
            img.save(path, "JPEG")
            return path
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
    return None

def process_book(row):
    """Processa um livro: tenta achar capa e salvar"""
    book_id = row["book_id"]
    title = str(row["title"])
    author = str(row["authors"]).split(",")[0]
    isbn = str(row["isbn13"]) if pd.notnull(row["isbn13"]) else None

    filename = f"{book_id}_{title[:50].replace('/', '_')}.jpg"

    # 3) Google Books via título+autor
    url = get_googlebooks_cover(title=title, author=author)
    if url:
        path = download_and_resize(url, filename)
        if path:
            return (book_id, title, author, isbn, path)

    # Nenhuma capa encontrada
    return (book_id, title, author, isbn, None)


# --- Script principal ---
if __name__ == "__main__":
    books = pd.read_csv("dataset/books.csv", dtype={"isbn13": str})

    done = 0
    total = len(books)
    results = []

    # Usa 10 threads em paralelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_book, row) for _, row in books.iterrows()]
        for future in as_completed(futures):
            results.append(future.result())

            done += 1
            if done % 100 == 0 or done == total:  # imprime a cada 100 livros ou no final
                print(f"[{done}/{total}] capas processadas...")

    # Salva controle em CSV
    df_covers = pd.DataFrame(results, columns=["book_id", "title", "author", "isbn13", "cover_path"])
    df_covers.to_csv("covers.csv", index=False)

    print("✅ Download concluído! Resultados em covers.csv")
