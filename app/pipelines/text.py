"""Text generation pipeline with OpenAI integration."""
import requests
from typing import Any, Dict, List
from ..config import OPENAI_API_KEY

def call_openai_api(messages, model="gpt-4", max_tokens=1000, temperature=0.7):
    """Make direct API call to OpenAI using requests."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return None

# Enhanced channel-specific prompt templates with multimodal features
CHANNEL_PROMPTS = {
    "email": """Create compelling email marketing copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}
Audience: {audience_context}
Brand Assets: {brand_context}

Requirements:
- Subject line (max 50 characters) - optimized for open rates
- Email body (max 200 words) - {content_length} format
- Clear call-to-action with urgency
- {brand_voice} tone throughout
- Mobile-optimized format
- Personalization elements for {age_range} audience
- NO excessive emojis - keep it professional
- Include social proof or testimonials if relevant""",

    "instagram": """Create Instagram post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}
Audience: {audience_context}
Brand Assets: {brand_context}

Requirements:
- Caption (max 2,200 characters) - {content_length} format
- 8-12 relevant hashtags (mix of popular and niche)
- Engaging hook in first line
- Storytelling approach with emotional connection
- {brand_voice} brand voice consistency
- Call-to-action (swipe up, visit link, comment)
- MINIMAL emojis - use sparingly and strategically
- Include user-generated content prompts
- Optimize for {age_range} {gender} audience""",

    "facebook": """Create Facebook post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}
Audience: {audience_context}
Brand Assets: {brand_context}

Requirements:
- Post text (max 500 characters) - {content_length} format
- Engaging opening that stops scrolling
- Clear value proposition
- Community-focused tone
- Strong call-to-action
- Encourage sharing and engagement
- NO excessive emojis - keep it clean and professional
- Include questions to encourage comments
- Optimize for {age_range} {gender} audience in {location}
- Use {brand_values} as core messaging themes""",

    "twitter": """Create Twitter post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}
Audience: {audience_context}
Brand Assets: {brand_context}

Requirements:
- Tweet text (max 280 characters) - {content_length} format
- Attention-grabbing opening
- Clear, concise message
- Relevant hashtags (max 2-3)
- {brand_voice} tone
- Call-to-action if space allows
- MINIMAL emojis - use 1-2 maximum
- Optimize for {age_range} audience
- Include trending topics if relevant
- Thread potential for longer content"""
}


def generate_text(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate marketing copy using OpenAI GPT-4 with multimodal features."""
    channel = input_data.get("channel", "general")
    title = input_data.get("title", "Your Campaign")
    brief = input_data.get("brief", "")
    brand_profile_id = input_data.get("brand_profile_id", "demo")
    
    # Extract new multimodal features
    audience_target = input_data.get("audience_target", {})
    brand_assets = input_data.get("brand_assets", {})
    content_length = input_data.get("content_length", "medium")
    generate_variations = input_data.get("generate_variations", True)
    include_emoji = input_data.get("include_emoji", False)
    
    # Build audience context
    audience_context = f"Age: {audience_target.get('age_range', '25-45')}, Gender: {audience_target.get('gender', 'all')}, Location: {audience_target.get('location', 'global')}, Interests: {', '.join(audience_target.get('interests', []))}"
    
    # Build brand context
    brand_context = f"Voice: {brand_assets.get('brand_voice', 'professional')}, Tone: {brand_assets.get('tone', 'neutral')}, Values: {', '.join(brand_assets.get('brand_values', []))}, Colors: {brand_assets.get('primary_color', '#10b981')}"
    
    # Get channel-specific prompt template
    prompt_template = CHANNEL_PROMPTS.get(channel, CHANNEL_PROMPTS["email"])
    prompt = prompt_template.format(
        title=title,
        brief=brief,
        brand_profile_id=brand_profile_id,
        audience_context=audience_context,
        brand_context=brand_context,
        content_length=content_length,
        age_range=audience_target.get('age_range', '25-45'),
        gender=audience_target.get('gender', 'all'),
        location=audience_target.get('location', 'global'),
        brand_voice=brand_assets.get('brand_voice', 'professional'),
        brand_values=', '.join(brand_assets.get('brand_values', []))
    )
    
    try:
        messages = [
            {"role": "system", "content": "You are a professional marketing copywriter with expertise in creating compelling, conversion-focused content across all digital channels. You understand audience psychology, brand consistency, and platform optimization."},
            {"role": "user", "content": prompt}
        ]
        
        response = call_openai_api(messages, model="gpt-4", max_tokens=1500, temperature=0.8)
        
        if response and "choices" in response:
            primary_content = response["choices"][0]["message"]["content"].strip()
            
            # Generate variations if requested
            variations = []
            if generate_variations:
                variations = generate_content_variations(
                    channel, title, brief, audience_context, brand_context, 
                    content_length, brand_voice=brand_assets.get('brand_voice', 'professional')
                )
            
            # Calculate engagement score
            engagement_score = calculate_engagement_score(primary_content, channel, audience_target)
            
            return {
                "primary": primary_content,
                "variations": variations,
                "engagement_score": engagement_score,
                "optimization_tips": generate_optimization_tips(channel, primary_content, audience_target)
            }
        else:
            # Fallback to mock response if API call fails
            return {
                "primary": f"Generated copy for {channel}: {title} — {brief}\n\n[Note: OpenAI API call failed. This is a mock response.]",
                "variations": [],
                "engagement_score": 0.7,
                "optimization_tips": ["Consider A/B testing different headlines", "Add more specific call-to-actions"]
            }
    except Exception as e:
        # Fallback to mock response on error
        return {
            "primary": f"Generated copy for {channel}: {title} — {brief}\n\n[Error: {str(e)}]",
            "variations": [],
            "engagement_score": 0.6,
            "optimization_tips": ["Check your inputs and try again"]
        }


def generate_content_variations(channel: str, title: str, brief: str, audience_context: str, brand_context: str, content_length: str, brand_voice: str = "professional") -> List[str]:
    """Generate 2-3 variations of the content for A/B testing."""
    variation_prompts = [
        f"Create a {brand_voice} variation of this {channel} content with a more emotional appeal: {brief}",
        f"Create a {brand_voice} variation of this {channel} content with a more data-driven approach: {brief}",
        f"Create a {brand_voice} variation of this {channel} content with a more urgent tone: {brief}"
    ]
    
    variations = []
    try:
        for i, var_prompt in enumerate(variation_prompts[:2]):  # Limit to 2 variations
            messages = [
                {"role": "system", "content": f"You are creating a {content_length} {channel} marketing variation. Keep the same core message but adjust the approach."},
                {"role": "user", "content": var_prompt}
            ]
            
            response = call_openai_api(messages, model="gpt-4", max_tokens=800, temperature=0.9)
            if response and "choices" in response:
                variations.append(response["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    
    return variations


def calculate_engagement_score(content: str, channel: str, audience_target: dict) -> float:
    """Calculate predicted engagement score based on content analysis."""
    score = 0.7  # Base score
    
    # Length optimization
    if channel == "twitter" and len(content) < 200:
        score += 0.1
    elif channel in ["facebook", "instagram"] and 100 < len(content) < 400:
        score += 0.1
    
    # Hashtag optimization
    hashtag_count = content.count('#')
    if channel == "instagram" and 5 <= hashtag_count <= 12:
        score += 0.1
    elif channel == "twitter" and 1 <= hashtag_count <= 3:
        score += 0.1
    
    # Call-to-action presence
    cta_words = ["click", "visit", "shop", "buy", "learn", "discover", "try", "get"]
    if any(word in content.lower() for word in cta_words):
        score += 0.1
    
    return min(1.0, score)


def generate_optimization_tips(channel: str, content: str, audience_target: dict) -> List[str]:
    """Generate optimization tips based on content analysis."""
    tips = []
    
    if len(content) < 50:
        tips.append("Consider adding more details to increase engagement")
    
    if not any(word in content.lower() for word in ["click", "visit", "shop", "buy"]):
        tips.append("Add a clear call-to-action to drive conversions")
    
    if channel == "instagram" and content.count('#') < 5:
        tips.append("Add more relevant hashtags to increase discoverability")
    
    if channel == "twitter" and len(content) > 250:
        tips.append("Consider shortening for better Twitter engagement")
    
    if audience_target.get('age_range') == '18-24' and not any(word in content.lower() for word in ["trending", "viral", "now"]):
        tips.append("Consider adding trending language for younger audience")
    
    return tips[:3]  # Return top 3 tips
