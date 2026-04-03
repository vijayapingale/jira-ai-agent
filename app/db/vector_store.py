class DummyVectorDB:
    def add_texts(self, texts, metadatas=None):
        print("Stored:", texts[0][:50])

vector_db = DummyVectorDB()