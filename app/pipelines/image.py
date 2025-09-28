"""Image generation pipeline with DALL-E integration."""
import requests
import boto3
import httpx
from typing import Any, Dict
from urllib.parse import quote_plus
from ..config import OPENAI_API_KEY, S3_BUCKET, S3_KEY, S3_SECRET, S3_REGION

# Initialize S3 client for image storage
s3_client = None
if S3_BUCKET and S3_KEY and S3_SECRET:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
        region_name=S3_REGION
    )

def call_dalle_api(prompt, size="1024x1024", quality="standard", n=1):
    """Make direct API call to DALL-E using requests."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"DALL-E API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"DALL-E API call failed: {e}")
        return None

# Channel-specific image prompts and dimensions
CHANNEL_IMAGE_CONFIG = {
    "email": {
        "prompt_template": "Professional marketing image for email campaign: {title} - {brief}. Clean, modern design with clear typography.",
        "width": 600,
        "height": 400,
        "style": "professional, clean, modern"
    },
    "instagram": {
        "prompt_template": "Instagram post image for: {title} - {brief}. Eye-catching, social media optimized, square format.",
        "width": 1080,
        "height": 1080,
        "style": "vibrant, social media, engaging"
    },
    "facebook": {
        "prompt_template": "Facebook post image for: {title} - {brief}. Social media friendly, engaging visual.",
        "width": 1200,
        "height": 630,
        "style": "social media, engaging, professional"
    },
    "twitter": {
        "prompt_template": "Twitter post image for: {title} - {brief}. Clean, impactful design for social media.",
        "width": 1200,
        "height": 675,
        "style": "clean, impactful, social media"
    }
}


def generate_image(input_data: Dict[str, Any]) -> str:
    """Generate marketing images using DALL-E."""
    channel = input_data.get("channel", "general")
    title = input_data.get("title", "Your Campaign")
    brief = input_data.get("brief", "")

    # Get channel-specific configuration
    config = CHANNEL_IMAGE_CONFIG.get(channel, CHANNEL_IMAGE_CONFIG["email"])

    # Create image prompt
    prompt = config["prompt_template"].format(title=title, brief=brief)

    try:
        if OPENAI_API_KEY and OPENAI_API_KEY.strip():
            # Generate image using DALL-E
            response = call_dalle_api(
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            if response and "data" in response and len(response["data"]) > 0:
                image_url = response["data"][0]["url"]
                
                # Store image in S3 if configured
                if s3_client:
                    stored_url = store_image_in_s3(image_url, f"{channel}_{title.replace(' ', '_')}")
                    return stored_url
                else:
                    return image_url
            else:
                # Fallback to placeholder if API call fails
                return get_placeholder_image(channel, title)
        else:
            # Fallback to placeholder if no API key
            return get_placeholder_image(channel, title)

    except Exception as e:
        # Fallback to placeholder on error
        return get_placeholder_image(channel, title, str(e))


def store_image_in_s3(image_url: str, filename: str) -> str:
    """Download image from URL and store in S3."""
    try:
        # Download image
        with httpx.Client() as client:
            response = client.get(image_url)
            response.raise_for_status()
            image_data = response.content
        
        # Upload to S3
        s3_key = f"generated-images/{filename}.png"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_data,
            ContentType='image/png'
        )
        
        # Return S3 URL
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
    except Exception as e:
        # Return original URL if S3 upload fails
        return image_url


def get_placeholder_image(channel: str, title: str, error: str = None) -> str:
    """Get placeholder image URL."""
    # Create a more professional placeholder without error messages
    label = quote_plus(f"{channel.title()}: {title}")
    # Use a clean placeholder service
    return f"https://via.placeholder.com/600x400/3b82f6/ffffff?text={label}"
