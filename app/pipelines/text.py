"""Text generation pipeline with OpenAI integration."""
import requests
from typing import Any, Dict
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

# Channel-specific prompt templates
CHANNEL_PROMPTS = {
    "email": """Create compelling email marketing copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}

Requirements:
- Subject line (max 50 characters)
- Email body (max 200 words)
- Clear call-to-action
- Professional but engaging tone
- Mobile-friendly format""",

    "instagram": """Create Instagram post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}

Requirements:
- Caption (max 2,200 characters)
- 5-10 relevant hashtags
- Engaging hook in first line
- Storytelling approach
- Brand voice consistency""",

    "facebook": """Create Facebook post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}

Requirements:
- Post text (max 500 characters)
- Engaging opening
- Clear value proposition
- Call-to-action
- Community-focused tone""",

    "twitter": """Create Twitter post copy for the following campaign:

Title: {title}
Brief: {brief}
Brand Profile: {brand_profile_id}

Requirements:
- Tweet text (max 280 characters)
- Attention-grabbing opening
- Clear message
- Relevant hashtags (max 3)
- Concise and impactful"""
}


def generate_text(input_data: Dict[str, Any]) -> str:
    """Generate marketing copy using OpenAI GPT-4."""
    channel = input_data.get("channel", "general")
    title = input_data.get("title", "Your Campaign")
    brief = input_data.get("brief", "")
    brand_profile_id = input_data.get("brand_profile_id", "demo")
    
    # Get channel-specific prompt template
    prompt_template = CHANNEL_PROMPTS.get(channel, CHANNEL_PROMPTS["email"])
    prompt = prompt_template.format(
        title=title,
        brief=brief,
        brand_profile_id=brand_profile_id
    )
    
    try:
        messages = [
            {"role": "system", "content": "You are a professional marketing copywriter with expertise in creating compelling, conversion-focused content across all digital channels."},
            {"role": "user", "content": prompt}
        ]
        
        response = call_openai_api(messages, model="gpt-4", max_tokens=1000, temperature=0.7)
        
        if response and "choices" in response:
            return response["choices"][0]["message"]["content"].strip()
        else:
            # Fallback to mock response if API call fails
            return f"Generated copy for {channel}: {title} — {brief}\n\n[Note: OpenAI API call failed. This is a mock response.]"
    except Exception as e:
        # Fallback to mock response on error
        return f"Generated copy for {channel}: {title} — {brief}\n\n[Error: {str(e)}]"
