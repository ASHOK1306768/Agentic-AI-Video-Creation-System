# Agentic AI Social Media Video Automation

An autonomous, multi-agent AI system that converts **one single prompt** into a fully produced, quality-controlled, SEO-optimized vertical video (9:16) and automatically schedules/publishes it to **YouTube Shorts** and **Instagram Reels**.

---

## 🏗️ System Architecture

```text
USER PROMPT
     ↓
n8n WEBHOOK
     ↓
CONTENT PLANNING AGENT (Strategy, audience, duration, hook)
     ↓
SCRIPT GENERATION AGENT (Engaging narrative with [SCENE BREAK])
     ↓
SCENE EXTRACTION & SPLIT (Per-scene text, duration, visual keywords)
     ↓
VISUAL ASSET RETRIEVAL (Pexels / Pixabay stock media + procedural fallback)
     ↓
VOICEOVER NARRATION (Google Cloud TTS / Edge-TTS / Piper)
     ↓
SUBTITLE GENERATION & BURN-IN (.srt Whisper captions)
     ↓
FFMPEG & MOVIEPY VIDEO COMPOSER (1080x1920 9:16 Vertical MP4)
     ↓
QUALITY CONTROL AGENT (Pass/Fail file integrity & content audit)
     ↓
SEO AGENT (YouTube Title/Tags & Instagram Caption/Hashtags)
     ↓
SCHEDULE & WAIT (Target publish date & time)
     ↓
YOUTUBE & INSTAGRAM PUBLISHING (Official APIs)
     ↓
EMAIL NOTIFICATION & WEBHOOK RESPONSE
```

---

## 📁 Project Structure

```
AI Video Automation/
│
├── docker-compose.yml           # Multi-container orchestration (n8n, python-worker, ollama)
├── Dockerfile                   # Python worker container with FFmpeg & MoviePy
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for API keys and credentials
├── .env                         # Active configuration
├── .gitignore                   # Git ignore for secrets and media outputs
├── README.md                    # Project manual & setup guide
├── test_pipeline.py             # Automated verification suite
│
├── scripts/                     # Modular Python Microservice
│   ├── config.py                # Environment and path settings
│   ├── script_generator.py      # LLM script generation
│   ├── scene_extractor.py       # Scene segmentation & duration calculator
│   ├── asset_downloader.py      # Pexels/Pixabay stock media retriever
│   ├── voice_generator.py       # Neural TTS voiceover generator
│   ├── video_composer.py        # 9:16 vertical video & subtitle rendering
│   ├── quality_agent.py         # Automated QA & validation agent
│   ├── seo_agent.py             # YouTube & Instagram SEO metadata generator
│   ├── app.py                   # Flask REST API entry point
│   └── Dockerfile               # Localized Dockerfile
│
├── n8n-workflows/
│   └── video-agent.json         # Complete 37-node exportable n8n workflow
│
└── outputs/                     # Media generation output directories
    ├── visuals/                 # Downloaded / generated scene images
    ├── audio/                   # Voiceover audio files (.mp3, .wav)
    ├── subtitles/               # Generated subtitle files (.srt)
    └── videos/                  # Final compiled MP4 videos
```

---

## 🚀 Quick Start Guide

### Option A: Run with Docker Compose (Recommended)

1. **Start Docker Desktop** on your machine.
2. Open terminal in the project directory:
   ```bash
   # Start all services in the background
   docker compose up -d
   ```
3. Check running containers:
   ```bash
   docker compose ps
   ```
4. Access the web services:
   - **n8n Workflow Editor**: [http://localhost:5678](http://localhost:5678) *(User: admin | Pass: secure_password)*
   - **Ollama LLM API**: [http://localhost:11434](http://localhost:11434)
   - **Python Worker API**: [http://localhost:5000](http://localhost:5000)

5. Pull the local LLM model into Ollama (takes ~2 minutes):
   ```bash
   docker exec video-agent-ollama ollama pull mistral
   ```

---

### Option B: Run Directly with Python (Local Testing)

If you wish to test or run without Docker:
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the automated test suite:
   ```bash
   python test_pipeline.py
   ```
3. Start the Flask microservice:
   ```bash
   python scripts/app.py
   ```

---

## 🔑 Free APIs & Credentials Setup

The system is designed to run **100% free with no credit card required**:

| Service | Free Tier Allowance | How to Get |
| :--- | :--- | :--- |
| **Ollama** | Unlimited local offline LLM | [ollama.ai](https://ollama.ai) (Runs locally via container) |
| **Pexels** | Unlimited stock photos & videos | [pexels.com/api](https://www.pexels.com/api/) (Instant key) |
| **Pixabay** | Unlimited stock photos & royalty-free music | [pixabay.com/api](https://pixabay.com/api/) |
| **Google Cloud TTS** | 1,000,000 characters/month free | [cloud.google.com](https://cloud.google.com) → TTS API |
| **Edge-TTS / Piper** | 100% free offline neural speech | Built-in fallback in `scripts/voice_generator.py` |

Edit your `.env` file to add your API keys:
```env
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
```

---

## 🔄 Importing the 37-Node Workflow into n8n

1. Open **n8n** in your browser at [http://localhost:5678](http://localhost:5678).
2. Click on **Workflows** → **Add Workflow** (or the **+** button).
3. In the top right menu (`...`), click **Import from File**.
4. Select `n8n-workflows/video-agent.json`.
5. You will see all 37 nodes organized into the 11 pipeline stages:
   - **Module 1**: Webhook & User Prompt extraction
   - **Module 2**: Planning Agent & Script Agent
   - **Module 3**: Scene Agent & Loop Over Items
   - **Module 4**: Visual Prompt Agent & Stock Download
   - **Module 5**: Voiceover (TTS) & Whisper Subtitles
   - **Module 6**: FFmpeg 9:16 Video Composition
   - **Module 7**: Quality Control & Pass/Fail Loop
   - **Module 8**: SEO Optimization Agent
   - **Module 9**: Publishing Time & Wait Scheduling
   - **Module 10**: YouTube & Instagram Official Publishing
   - **Module 11**: Gmail Notifications & Webhook Response

---

## 📡 Testing the System via Webhook

Trigger the full automation with a single HTTP POST request:

```bash
curl -X POST http://localhost:5678/webhook/video-agent \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Create a 60-second Instagram Reel about Artificial Intelligence in Education",
    "publish_date": "2026-09-25",
    "publish_time": "19:00"
  }'
```

Or trigger the Python worker API directly:
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "The Future of Quantum Computing"}'
```

The compiled video will be saved in `outputs/videos/` as a high-definition 9:16 MP4 video!
