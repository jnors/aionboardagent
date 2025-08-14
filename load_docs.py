import os
import json
import glob
import tqdm
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    TextLoader,
)

def build_vector_index():
    # Supported file types and loaders
    file_types = {
        ".pdf": UnstructuredPDFLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".md": UnstructuredMarkdownLoader,
        ".html": UnstructuredHTMLLoader,
        ".txt": TextLoader,
    }

    all_docs = []

    # Gather all matching files
    all_paths = []
    for ext in file_types.keys():
        all_paths.extend(glob.glob(f"data/docs/**/*{ext}", recursive=True))

    print(f"🔍 Found {len(all_paths)} files")

    for path in tqdm.tqdm(all_paths, desc="📄 Processing files"):
        ext = os.path.splitext(path)[-1].lower()
        loader_cls = file_types.get(ext)

        if not loader_cls:
            print(f"⚠️ No loader for file: {path}")
            continue

        try:
            loader = loader_cls(path, **({"strategy": "fast"} if ext == ".pdf" else {}))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = os.path.basename(path)
            all_docs.extend(docs)
            print(f"✅ Loaded: {os.path.basename(path)}")
        except Exception as e:
            print(f"⚠️ Failed to load {os.path.basename(path)} with {loader_cls.__name__}: {e}")
            # Optional fallback
            try:
                loader = TextLoader(path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = os.path.basename(path)
                all_docs.extend(docs)
                print(f"🟡 Fallback succeeded for: {os.path.basename(path)}")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed for {os.path.basename(path)}: {fallback_error}")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(all_docs)

    if not chunks:
        print("⚠️ No document chunks were created. Check if files were successfully loaded and parsed.")
        return

    # Save file metadata for UI sidebar
    file_metadata = {
        "files": list(set(doc.metadata.get("source", "unknown") for doc in all_docs)),
        "timestamp": datetime.now().isoformat(),
        "count": len(all_docs)
    }

    os.makedirs("data", exist_ok=True)
    with open("data/embedding_metadata.json", "w") as f:
        json.dump(file_metadata, f, indent=2)

    # Build and save FAISS index
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = FAISS.from_documents(chunks, embeddings)
    index.save_local("data/embeddings")

    print("✅ Embedding complete!")

if __name__ == "__main__":
    build_vector_index()
