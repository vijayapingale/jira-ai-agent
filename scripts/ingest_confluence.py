import os
from app.ingestion.confluence_loader import fetch_confluence_pages
from app.ingestion.chunking import chunk_text
from app.db.vector_store import vector_db

def main():
    print("Fetching Confluence pages...")

    pages = fetch_confluence_pages()

    for page in pages.get("results", []):
        title = page["title"]
        content = str(page)  # simplify for now

        chunks = chunk_text(content)

        for chunk in chunks:
            vector_db.add_texts([chunk], metadatas=[{"title": title}])

    print("✅ Ingestion completed")

if __name__ == "__main__":
    main()