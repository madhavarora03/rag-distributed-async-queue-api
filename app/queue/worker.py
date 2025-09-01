from typing import cast
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from pydantic import SecretStr

from ..core.config import settings

client = OpenAI(api_key=settings.openai_api_key)
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=cast(SecretStr, settings.openai_api_key)
)

vector_db = QdrantVectorStore.from_existing_collection(
    url=settings.qdrant_uri,
    collection_name="rag-daq",
    embedding=embedding_model
)


def process_query(query: str):
    print("Searching Chunks for query:", query)
    search_results = vector_db.similarity_search(query=query)

    context = "\n\n\n".join([
        f"Page Content: {res.page_content}\n"
        f"Page Number: {res.metadata.get('page_label')}\n"
        f"File Location: {res.metadata.get('source')}"
        for res in search_results
    ])

    SYSTEM_PROMPT = f"""
You are a helpful AI assistant answering queries based only on the following \
context:

{context}
"""
    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    return chat_completion.choices[0].message.content
