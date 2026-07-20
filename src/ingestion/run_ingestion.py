from ingestion.pipeline import ingest_all_pdfs
from ingestion.chunkers.recursive import RecursiveChunker

chunker = RecursiveChunker(
    chunk_size=500,
    overlap=100
)

results = ingest_all_pdfs(chunker)

print("\nIngestion complete!\n")

for pdf, chunks in results.items():
    print(f"{pdf}: {chunks} chunks")