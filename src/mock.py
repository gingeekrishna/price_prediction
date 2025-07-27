# src/mocks.py

class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 1536


class DummyChatCompletion:
    def create(self, **kwargs):
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a dummy explanation because the API quota was exceeded."
                    }
                }
            ]
        }
