"""Content scoring pipeline with LLM-based evaluation."""
from openai import OpenAI
from typing import Any, Dict, List
from ..config import OPENAI_API_KEY

# Initialize OpenAI client (lazy initialization)
client = None

def get_openai_client():
    """Get OpenAI client with lazy initialization."""
    global client
    if client is None and OPENAI_API_KEY and OPENAI_API_KEY.strip():
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            print(f"Warning: OpenAI client initialization failed: {e}")
            client = None
    return client


def score_content(content: Dict[str, Any]) -> Dict[str, Any]:
    """Score content using LLM-based evaluation."""
    copies = content.get("copies", [])
    images = content.get("images", [])
    
    # Calculate basic metrics
    total_copies = len(copies)
    total_images = len(images)
    
    # If no OpenAI client, return basic scoring
    openai_client = get_openai_client()
    if not openai_client:
        return {
            "overall_score": round(min(1.0, 0.5 + 0.05 * total_copies + 0.02 * total_images), 2),
            "copy_score": 0.7,
            "image_score": 0.6,
            "brand_consistency": 0.8,
            "engagement_potential": 0.7,
            "metrics": {
                "total_copies": total_copies,
                "total_images": total_images,
                "avg_copy_length": sum(len(copy) for copy in copies) / max(total_copies, 1)
            }
        }
    
    try:
        # Evaluate copy quality
        copy_scores = []
        for i, copy in enumerate(copies):
            copy_score = evaluate_copy_quality(copy, i)
            copy_scores.append(copy_score)
        
        # Evaluate image quality
        image_scores = []
        for i, image_url in enumerate(images):
            image_score = evaluate_image_quality(image_url, i)
            image_scores.append(image_score)
        
        # Calculate overall scores
        avg_copy_score = sum(copy_scores) / max(len(copy_scores), 1)
        avg_image_score = sum(image_scores) / max(len(image_scores), 1)
        
        # Brand consistency evaluation
        brand_consistency = evaluate_brand_consistency(copies)
        
        # Engagement potential
        engagement_potential = evaluate_engagement_potential(copies)
        
        # Overall score (weighted average)
        overall_score = (
            avg_copy_score * 0.4 +
            avg_image_score * 0.3 +
            brand_consistency * 0.2 +
            engagement_potential * 0.1
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "copy_score": round(avg_copy_score, 2),
            "image_score": round(avg_image_score, 2),
            "brand_consistency": round(brand_consistency, 2),
            "engagement_potential": round(engagement_potential, 2),
            "metrics": {
                "total_copies": total_copies,
                "total_images": total_images,
                "avg_copy_length": sum(len(copy) for copy in copies) / max(total_copies, 1),
                "copy_scores": copy_scores,
                "image_scores": image_scores
            }
        }
        
    except Exception as e:
        # Fallback to basic scoring on error
        return {
            "overall_score": round(min(1.0, 0.5 + 0.05 * total_copies + 0.02 * total_images), 2),
            "copy_score": 0.7,
            "image_score": 0.6,
            "brand_consistency": 0.8,
            "engagement_potential": 0.7,
            "error": str(e),
            "metrics": {
                "total_copies": total_copies,
                "total_images": total_images,
                "avg_copy_length": sum(len(copy) for copy in copies) / max(total_copies, 1)
            }
        }


def evaluate_copy_quality(copy: str, index: int) -> float:
    """Evaluate the quality of a single copy using LLM."""
    try:
        prompt = f"""
Evaluate this marketing copy on a scale of 0-1 for the following criteria:

Copy: {copy}

Rate each criterion (0-1):
1. Clarity and readability
2. Compelling and engaging
3. Clear call-to-action
4. Appropriate length
5. Professional tone

Provide scores as: clarity: X, compelling: X, cta: X, length: X, tone: X
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a marketing expert evaluating copy quality. Respond with only the scores in the requested format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        # Parse scores from response
        text = response.choices[0].message.content
        scores = []
        for criterion in ["clarity", "compelling", "cta", "length", "tone"]:
            if f"{criterion}:" in text:
                try:
                    score = float(text.split(f"{criterion}:")[1].split(",")[0].strip())
                    scores.append(score)
                except:
                    scores.append(0.7)  # Default score
            else:
                scores.append(0.7)
        
        return sum(scores) / len(scores)
        
    except Exception:
        return 0.7  # Default score on error


def evaluate_image_quality(image_url: str, index: int) -> float:
    """Evaluate image quality (simplified for now)."""
    # For now, return a basic score based on URL validity
    if image_url and "placehold.co" not in image_url:
        return 0.8  # Real generated image
    else:
        return 0.5  # Placeholder image


def evaluate_brand_consistency(copies: List[str]) -> float:
    """Evaluate brand consistency across all copies."""
    try:
        prompt = f"""
Evaluate the brand consistency across these marketing copies on a scale of 0-1:

Copies:
{chr(10).join(f"{i+1}. {copy}" for i, copy in enumerate(copies))}

Consider:
- Consistent tone and voice
- Unified messaging
- Brand alignment
- Cohesive style

Provide a single score (0-1) for overall brand consistency.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a brand expert evaluating consistency. Respond with only a number between 0-1."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        # Extract score from response
        text = response.choices[0].message.content
        try:
            return float(text.strip())
        except:
            return 0.8  # Default score
            
    except Exception:
        return 0.8  # Default score on error


def evaluate_engagement_potential(copies: List[str]) -> float:
    """Evaluate engagement potential of the copies."""
    try:
        prompt = f"""
Evaluate the engagement potential of these marketing copies on a scale of 0-1:

Copies:
{chr(10).join(f"{i+1}. {copy}" for i, copy in enumerate(copies))}

Consider:
- Emotional appeal
- Call-to-action strength
- Social media optimization
- Shareability
- Conversion potential

Provide a single score (0-1) for overall engagement potential.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a marketing expert evaluating engagement. Respond with only a number between 0-1."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        # Extract score from response
        text = response.choices[0].message.content
        try:
            return float(text.strip())
        except:
            return 0.7  # Default score
            
    except Exception:
        return 0.7  # Default score on error
