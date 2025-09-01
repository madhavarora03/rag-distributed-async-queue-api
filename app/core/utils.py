import asyncio
import os
import tempfile
import uuid
from typing import Tuple, cast

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import SecretStr

from ..services.db_service import JobStatus, update_job
from ..services.r2_client import r2_client
from .config import settings


def save_to_tmp(file: bytes, file_name: str | None) -> Tuple[str, str]:
    """
    Save bytes securely in the system's temp dir with a unique name.
    Returns the absolute file path.
    """
    tmp_dir = tempfile.gettempdir()
    base_name = os.path.basename(file_name) if file_name else "uploaded_file"
    unique_name = f"{uuid.uuid4()}_{base_name}"

    file_path = os.path.join(tmp_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file)

    return file_path, unique_name


def save_to_r2(file_path: str) -> str:
    """Upload file to R2 and return object key. Raises on failure."""
    R2_BUCKET_NAME = settings.r2_bucket_name
    if not R2_BUCKET_NAME:
        raise ValueError("R2_BUCKET_NAME is not set")

    key = os.path.basename(file_path)

    try:
        r2_client.upload_file(file_path, R2_BUCKET_NAME, key)
        return key
    except Exception as e:
        # Log the error (or use your structured logger)
        print(f"[ERROR] Failed to upload {file_path} to R2: {e}")
        # Raise again so process_file can mark job as FAILED
        raise RuntimeError(f"Upload to R2 failed: {e}") from e


async def parse_pdf(file_path: str):
    """Load and chunk a PDF into LangChain documents."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=400)
    return splitter.split_documents(docs)


async def generate_embeddings_and_store(split_docs, job_id: str):
    """Generate embeddings and push into Qdrant."""
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=cast(SecretStr, settings.openai_api_key)
    )

    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url=settings.qdrant_uri,
        collection_name="rag-daq",
        embedding=embedding_model,
    )
    return vector_store


async def process_file(file_path: str, job_id: str):
    """Background job: Save to R2 → Parse PDF → Embeddings → Store in Qdrant"""
    try:
        # Step 1. Save to R2
        update_job(job_id, status=JobStatus.PROCESSING, step="Saving to R2")
        await asyncio.to_thread(save_to_r2, file_path)

        # Step 2. Parse PDF
        update_job(job_id, status=JobStatus.PROCESSING, step="Parsing PDF")
        split_docs = await parse_pdf(file_path)

        # Step 3. Generate embeddings
        update_job(job_id, status=JobStatus.PROCESSING,
                   step="Generating embeddings and storing in vector DB")
        await generate_embeddings_and_store(split_docs, job_id)

        # Step 4. Store in vector DB (done inside QdrantVectorStore call)
        update_job(job_id, status=JobStatus.DONE,
                   step="Complete")

        # Cleanup: remove temp file
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED, step="Error", error=str(e))


def start_process_file(file_path: str, job_id: str):
    """Wrapper to run async process_file in background."""
    import asyncio
    asyncio.run(process_file(file_path, job_id))
