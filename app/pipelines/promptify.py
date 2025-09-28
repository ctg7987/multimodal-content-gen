"""Prompt engineering pipeline with advanced prompt templates."""
from typing import Any, Dict
from jinja2 import Template

# Advanced prompt templates for different scenarios
PROMPT_TEMPLATES = {
    "default": """
You are a professional marketing copywriter creating content for {{ channel }}.

Campaign Details:
- Title: {{ title }}
- Brief: {{ brief }}
- Brand Profile: {{ brand_profile_id }}

Brand Context:
{{ brand_context }}

Create compelling marketing copy that:
1. Aligns with the brand voice and values
2. Speaks to the target audience
3. Includes a clear call-to-action
4. Is optimized for {{ channel }}
5. Drives engagement and conversions

Requirements:
- Channel-specific format and length
- Brand-consistent tone
- Compelling hook
- Clear value proposition
- Strong call-to-action
""",
    
    "email": """
Create an email marketing campaign for {{ title }}.

Campaign Brief: {{ brief }}
Brand Profile: {{ brand_profile_id }}

Brand Context:
{{ brand_context }}

Requirements:
- Subject line (max 50 characters)
- Email body (max 200 words)
- Clear call-to-action
- Professional but engaging tone
- Mobile-friendly format
- Personalization elements
""",
    
    "social_media": """
Create social media content for {{ channel }} about {{ title }}.

Campaign Brief: {{ brief }}
Brand Profile: {{ brand_profile_id }}

Brand Context:
{{ brand_context }}

Requirements:
- Platform-optimized format
- Engaging hook
- Visual storytelling elements
- Relevant hashtags
- Brand voice consistency
- Shareability focus
"""
}


def promptify(input_data: Dict[str, Any]) -> str:
    """Generate optimized prompts using Jinja2 templates."""
    title = input_data.get("title", "Untitled")
    brief = input_data.get("brief", "")
    channel = input_data.get("channel", "general")
    brand_profile_id = input_data.get("brand_profile_id", "demo")
    brand_context = input_data.get("brand_context", "No specific brand context provided.")
    
    # Select appropriate template
    if channel in ["email"]:
        template_key = "email"
    elif channel in ["instagram", "facebook", "twitter"]:
        template_key = "social_media"
    else:
        template_key = "default"
    
    # Get template
    template_str = PROMPT_TEMPLATES.get(template_key, PROMPT_TEMPLATES["default"])
    template = Template(template_str)
    
    # Render template with context
    try:
        prompt = template.render(
            title=title,
            brief=brief,
            channel=channel,
            brand_profile_id=brand_profile_id,
            brand_context=brand_context
        )
        return prompt.strip()
    except Exception as e:
        # Fallback to simple prompt
        return f"Create marketing content for {channel}: {title} - {brief}"
