"""RAG retrieval pipeline with Pinecone vector store."""
import requests
import pinecone
from typing import Any, Dict, List
from ..config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT

def call_openai_embeddings_api(text, model="text-embedding-ada-002"):
    """Make direct API call to OpenAI embeddings using requests."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": model
        }
        
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OpenAI embeddings API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"OpenAI embeddings API call failed: {e}")
        return None

# Initialize Pinecone
pinecone_client = None
if PINECONE_API_KEY:
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_client = pc.Index("brand-knowledge")
    except Exception as e:
        print(f"Warning: Pinecone initialization failed: {e}")
        pinecone_client = None

# Sample brand knowledge base (in production, this would be populated from documents)
BRAND_KNOWLEDGE = {
    "demo": {
        "brand_voice": "Professional, friendly, and approachable",
        "target_audience": "Tech-savvy professionals aged 25-45",
        "key_messages": ["Innovation", "Quality", "Customer-first approach"],
        "tone": "Conversational yet professional",
        "brand_values": ["Trust", "Innovation", "Excellence"]
    },
    "tech_startup": {
        "brand_voice": "Innovative, energetic, and forward-thinking",
        "target_audience": "Early adopters and tech enthusiasts",
        "key_messages": ["Cutting-edge technology", "Disruption", "Future-focused"],
        "tone": "Bold and confident",
        "brand_values": ["Innovation", "Speed", "Disruption"]
    },
    "fashion_brand": {
        "brand_voice": "Trendy, stylish, and aspirational",
        "target_audience": "Fashion-conscious individuals aged 18-35",
        "key_messages": ["Style", "Self-expression", "Trend-setting"],
        "tone": "Inspirational and trendy",
        "brand_values": ["Creativity", "Individuality", "Style"]
    }
}


def rag_retrieve(input_data: Dict[str, Any]) -> str:
    """Retrieve relevant brand context using RAG."""
    brand_profile_id = input_data.get("brand_profile_id", "demo")
    title = input_data.get("title", "")
    brief = input_data.get("brief", "")
    
    # Get brand knowledge from static knowledge base
    brand_context = BRAND_KNOWLEDGE.get(brand_profile_id, BRAND_KNOWLEDGE["demo"])
    
    # If Pinecone is configured, perform vector search
    if pinecone_client and OPENAI_API_KEY:
        try:
            # Create query embedding
            query_text = f"{title} {brief}"
            query_embedding = get_embedding(query_text)
            
            # Search vector store
            results = pinecone_client.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True
            )
            
            # Combine results with brand context
            vector_context = "\n".join([
                match.metadata.get("text", "") for match in results.matches
            ])
            
            return f"""
Brand Context:
- Voice: {brand_context['brand_voice']}
- Target Audience: {brand_context['target_audience']}
- Key Messages: {', '.join(brand_context['key_messages'])}
- Tone: {brand_context['tone']}
- Values: {', '.join(brand_context['brand_values'])}

Relevant Knowledge:
{vector_context}
"""
        except Exception as e:
            # Fallback to static context if vector search fails
            pass
    
    # Return static brand context
    return f"""
Brand Context:
- Voice: {brand_context['brand_voice']}
- Target Audience: {brand_context['target_audience']}
- Key Messages: {', '.join(brand_context['key_messages'])}
- Tone: {brand_context['tone']}
- Values: {', '.join(brand_context['brand_values'])}

Campaign Context:
- Title: {title}
- Brief: {brief}
"""


def get_embedding(text: str) -> List[float]:
    """Get OpenAI embedding for text."""
    try:
        client = get_openai_client()
        if client:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        else:
            # Return zero vector if no client
            return [0.0] * 1536
    except Exception as e:
        # Return zero vector if embedding fails
        return [0.0] * 1536


def add_document_to_knowledge_base(text: str, metadata: Dict[str, Any]) -> bool:
    """Add document to Pinecone knowledge base."""
    if not pinecone_client or not OPENAI_API_KEY:
        return False
    
    try:
        # Get embedding
        embedding = get_embedding(text)
        
        # Add to Pinecone
        pinecone_client.upsert(
            vectors=[{
                "id": metadata.get("id", "doc_1"),
                "values": embedding,
                "metadata": metadata
            }]
        )
        return True
    except Exception as e:
        return False
