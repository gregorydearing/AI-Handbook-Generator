import os
import PyPDF2
import pdfplumber
from typing import List, Dict
import chromadb
from chromadb.config import Settings


class PDFProcessor:
    def __init__(self):
        """Initialize PDF processor with ChromaDB vector database"""
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(name="pdf_documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name="pdf_documents",
                metadata={"hnsw:space": "cosine"}
            )

        self.doc_counter = 0

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file using multiple methods for robustness"""
        text = ""

        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")

            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e2:
                raise Exception(f"Failed to extract text from PDF: {e2}")

        if not text.strip():
            raise Exception("No text could be extracted from the PDF")

        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context retrieval"""
        chunks = []
        words = text.split()

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def add_to_vectordb(self, text: str, source: str):
        """Add document chunks to vector database"""
        # Chunk the text
        chunks = self.chunk_text(text)

        # Prepare data for ChromaDB
        ids = [f"doc_{self.doc_counter}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk_id": i} for i in range(len(chunks))]

        # Add to collection
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

        self.doc_counter += 1
        print(f"Added {len(chunks)} chunks from {source}")

    def get_relevant_context(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant context from vector database"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(k, self.collection.count())
            )

            if not results['documents'] or not results['documents'][0]:
                return []

            # Format results
            contexts = []
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                contexts.append({
                    'text': doc,
                    'source': metadata.get('source', 'Unknown'),
                    'chunk_id': metadata.get('chunk_id', i)
                })

            return contexts
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    def clear_vectordb(self):
        """Clear the vector database"""
        try:
            self.chroma_client.delete_collection(name="pdf_documents")
            self.collection = self.chroma_client.create_collection(
                name="pdf_documents",
                metadata={"hnsw:space": "cosine"}
            )
            self.doc_counter = 0
            print("Vector database cleared")
        except Exception as e:
            print(f"Error clearing database: {e}")

    def get_all_text(self) -> str:
        """Get all text from the database (for comprehensive handbook generation)"""
        try:
            # Get all documents
            all_docs = self.collection.get()

            if not all_docs['documents']:
                return ""

            # Combine all chunks
            return "\n\n".join(all_docs['documents'])
        except Exception as e:
            print(f"Error getting all text: {e}")
            return ""
