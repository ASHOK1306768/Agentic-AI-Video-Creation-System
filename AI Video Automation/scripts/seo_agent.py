import json
import requests
from config import Config
from typing import Dict

class SEOAgent:
    """
    SEO Agent (Module 5 / Node 23 in n8n Student Manual).
    Generates platform-specific SEO metadata for YouTube Shorts and Instagram Reels.
    """
    def __init__(self):
        self.ollama_url = f"{Config.OLLAMA_BASE_URL}/api/generate"
        self.model = Config.LLM_MODEL

    def generate_seo(self, topic: str, script: str) -> Dict:
        prompt = f"""You are an expert Social Media SEO and Content Marketing Agent.
Analyze the following video topic and script.
Generate optimized content for YouTube Shorts and Instagram Reels.

Create:
1. SEO-friendly YouTube Title
2. YouTube Description
3. YouTube Keywords
4. YouTube Tags
5. Instagram Caption
6. Instagram Hashtags
7. Call to Action

TOPIC: {topic}
VIDEO SCRIPT: {script}

Return ONLY valid JSON matching this exact structure:
{{
  "youtube_title": "...",
  "youtube_description": "...",
  "youtube_keywords": ["keyword1", "keyword2"],
  "youtube_tags": ["tag1", "tag2"],
  "instagram_caption": "...",
  "instagram_hashtags": ["#tag1", "#tag2"],
  "call_to_action": "..."
}}"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            if response.status_code == 200:
                text_resp = response.json().get("response", "").strip()
                data = json.loads(text_resp)
                if "youtube_title" in data:
                    return data
        except Exception as e:
            print(f"[SEOAgent] Notice: Ollama API unreachable or invalid json ({e}). Using optimized metadata generator.")

        # Clean, engaging, platform-tailored fallback matching the Student Manual
        clean_topic = topic.replace('"', '').strip()
        return {
            "youtube_title": f"How {clean_topic} Is Changing Everything!",
            "youtube_description": f"Discover how {clean_topic} is transforming our daily life and workflow with AI automation. Like, subscribe, and share for more AI tutorials!",
            "youtube_keywords": [clean_topic, "AI", "Artificial Intelligence", "Technology", "Automation", "Future"],
            "youtube_tags": [clean_topic.lower(), "ai", "artificial intelligence", "tech", "automation", "future"],
            "instagram_caption": f"{clean_topic} is changing the game! What are your thoughts on this? Drop a comment below!",
            "instagram_hashtags": ["#AI", "#ArtificialIntelligence", "#TechTrends", "#Innovation", "#MachineLearning", "#FutureTech"],
            "call_to_action": "Follow for daily AI breakthroughs and automation guides!"
        }

if __name__ == "__main__":
    agent = SEOAgent()
    seo = agent.generate_seo("Artificial Intelligence in Education", "Sample script about learning with AI.")
    print(json.dumps(seo, indent=2))
