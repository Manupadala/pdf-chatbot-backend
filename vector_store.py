from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def create_embeddings(chunks):

    embeddings = model.encode(
        chunks
    )

    return embeddings


def build_faiss_index(
    embeddings
):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        np.array(
            embeddings,
            dtype="float32"
        )
    )

    return index


def save_index(index):

    faiss.write_index(
        index,
        "vectors/pdf.index"
    )

def search_chunks(
    query,
    chunks,
    index,
    top_k=3
):

    query_embedding = model.encode(
        [query]
    )

    distances, indices = index.search(
        np.array(
            query_embedding,
            dtype="float32"
        ),
        top_k
    )

    results = []

    for idx in indices[0]:
        results.append(
            chunks[idx]
        )

    return results