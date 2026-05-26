import os
import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import logging

logger = logging.getLogger(__name__)

class MedicalKnowledgeVectorMesh:
    def __init__(self):
        # Establish localized vector schema directory boundaries
        self.persist_directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "chroma_db"
        )
        
        # Initialize the production embedding transformer model
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize or attach to our persistent local Chroma database collection
        self.vector_store = Chroma(
            collection_name="clinical_knowledge_base",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Configure the text chunker for processing raw medical reference texts
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=150,
            length_function=len
        )

    async def ingest_raw_medical_text(self, document_title: str, raw_text: str) -> bool:
        """
        Splits text, generates vector embeddings, and registers chunks into ChromaDB.
        """
        try:
            if not raw_text.strip():
                return False
                
            # Breakdown monolithic string bodies into digestible context blocks
            chunks = self.text_splitter.split_text(raw_text)
            
            # Map metadata schemas for traceable data source tracking
            metadatas = [{"source": document_title, "chunk_id": str(uuid.uuid4())} for _ in chunks]
            
            # Persist directly into the Chroma index vector grid
            self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
            return True
        except Exception as e:
            logger.error(f"Ingestion pipeline failure on document '{document_title}': {str(e)}")
            return False

    def perform_semantic_knowledge_retrieval(self, query_prompt: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs a semantic vector similarity search against the ChromaDB collection.
        Returns the top 'K' most relevant text blocks.
        """
        try:
            # Execute low-latency similarity query matching
            matching_documents = self.vector_store.similarity_search(query_prompt, k=k)
            
            structured_results = []
            for doc in matching_documents:
                structured_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown Reference Module")
                })
            return structured_results
        except Exception as e:
            logger.error(f"Semantic search query execution crash: {str(e)}")
            return []