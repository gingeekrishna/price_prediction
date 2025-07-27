import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
# from langchain.embeddings import OpenAIEmbeddings


import sys
import os

# Add the parent directory (repo root) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from src.mock import DummyEmbeddings  # noqa: E402

# 1. Load documents from folder
docs_folder = "knowledge_docs"
all_docs = []

for filename in os.listdir(docs_folder):
    if filename.endswith(".txt"):
        loader = TextLoader(os.path.join(docs_folder, filename))
        docs = loader.load()
        all_docs.extend(docs)

# 2. Split large documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_docs = text_splitter.split_documents(all_docs)

# 3. Create embeddings
# embeddings = OpenAIEmbeddings()
embeddings = DummyEmbeddings()

# 4. Build FAISS index
vectorstore = FAISS.from_documents(split_docs, embeddings)

# 5. Save index locally
index_path = "faiss_index"
vectorstore.save_local(index_path)

print(f"✅ FAISS index saved at '{index_path}'")
