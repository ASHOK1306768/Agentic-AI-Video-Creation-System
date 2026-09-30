import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    # Directories
    BASE_DIR = Path(__file__).resolve().parent.parent
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIRECTORY", BASE_DIR / "outputs")).resolve()
    ASSETS_DIR = OUTPUT_DIR / "visuals"
    AUDIO_DIR = OUTPUT_DIR / "audio"
    SUBTITLES_DIR = OUTPUT_DIR / "subtitles"
    VIDEOS_DIR = OUTPUT_DIR / "videos"

    # LLM Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

    # API Keys & Auth
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")

    # Video Specifications (Vertical 9:16 format for Reels/Shorts/TikTok)
    VIDEO_FPS = int(os.getenv("VIDEO_FPS", "24"))
    VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
    VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
    VIDEO_QUALITY = os.getenv("VIDEO_QUALITY", "720")
    VIDEO_DURATION_SECONDS = int(os.getenv("VIDEO_DURATION_SECONDS", "60"))

    @classmethod
    def ensure_dirs(cls):
        """Ensure all output and media directories exist."""
        for d in [cls.OUTPUT_DIR, cls.ASSETS_DIR, cls.AUDIO_DIR, cls.SUBTITLES_DIR, cls.VIDEOS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate():
        Config.ensure_dirs()
        print("[Config] Configuration validated and directories initialized successfully.")

if __name__ == "__main__":
    Config.validate()
