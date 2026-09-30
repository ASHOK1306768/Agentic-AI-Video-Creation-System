from flask import Flask, request, jsonify
from config import Config
from script_generator import ScriptGenerator
from scene_extractor import SceneExtractor
from asset_downloader import AssetDownloader
from voice_generator import VoiceGenerator
from video_composer import VideoComposer
from quality_agent import QualityAgent
from seo_agent import SEOAgent
import traceback

app = Flask(__name__)

def create_video_from_prompt(prompt: str, duration_seconds: int = 60, title: str = ""):
    """
    End-to-end video pipeline executing all agentic modules.
    """
    try:
        print(f"\n==========================================")
        print(f"[App] Starting Agentic Video Generation: '{prompt}'")
        print(f"==========================================")
        
        # 1. Script Generation
        generator = ScriptGenerator()
        script_res = generator.generate(prompt, duration_seconds=duration_seconds)
        if script_res.get("status") != "success":
            return {"status": "error", "message": "Script generation failed"}
        script = script_res["script"]

        # 2. Scene Extraction
        extractor = SceneExtractor()
        scenes = extractor.extract_scenes(script)
        print(f"[App] Extracted {len(scenes)} scenes.")

        # 3. Visual Assets Retrieval
        downloader = AssetDownloader()
        scenes_with_images = downloader.download_images_for_scenes(scenes)

        # 4. Voiceover Audio
        voice_gen = VoiceGenerator()
        audio_path = voice_gen.generate_for_script(script, filename="voiceover.mp3")

        # 5. Video Composition (Vertical 9:16)
        video_title = title if title else prompt[:30]
        composer = VideoComposer()
        video_path = composer.compose_video(
            scenes_with_images=scenes_with_images,
            audio_path=audio_path,
            title=video_title
        )

        # 6. Quality Control Evaluation
        qc_result = QualityAgent.evaluate_project(
            script=script,
            scenes=scenes,
            visuals=scenes_with_images,
            audio_path=audio_path,
            video_path=video_path
        )

        # 7. SEO & Metadata Generation
        seo_agent = SEOAgent()
        seo_data = seo_agent.generate_seo(topic=prompt, script=script)

        return {
            "status": "success",
            "prompt": prompt,
            "script": script,
            "scenes": scenes_with_images,
            "audio_path": audio_path,
            "video_path": video_path,
            "qc_result": qc_result,
            "seo_data": seo_data
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "video-agent-python-worker"})

@app.route("/generate", methods=["POST"])
def generate_video():
    data = request.get_json() or {}
    prompt = data.get("prompt") or data.get("topic") or ""
    if not prompt:
        return jsonify({"error": "Missing prompt or topic in request body"}), 400

    duration = int(data.get("duration", data.get("duration_seconds", 60)))
    title = data.get("title", "")
    result = create_video_from_prompt(prompt=prompt, duration_seconds=duration, title=title)
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify(result), status_code

@app.route("/plan", methods=["POST"])
def plan_content():
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    return jsonify({
        "topic": prompt,
        "target_audience": "General Social Media Audience",
        "platform": "Instagram Reels & YouTube Shorts",
        "duration": 60,
        "tone": "Educational and Engaging",
        "style": "Short-form Video",
        "main_message": f"Essential insights into {prompt}",
        "hook_strategy": "Ask a provocative opening question"
    })

@app.route("/script", methods=["POST"])
def generate_script():
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    generator = ScriptGenerator()
    return jsonify(generator.generate(prompt))

@app.route("/scenes", methods=["POST"])
def extract_scenes():
    data = request.get_json() or {}
    script = data.get("script", "")
    extractor = SceneExtractor()
    return jsonify({"scenes": extractor.extract_scenes(script)})

@app.route("/visuals", methods=["POST"])
def get_visuals():
    data = request.get_json() or {}
    scenes = data.get("scenes", [])
    downloader = AssetDownloader()
    return jsonify({"visuals": downloader.download_images_for_scenes(scenes)})

@app.route("/voice", methods=["POST"])
def generate_voice():
    data = request.get_json() or {}
    script = data.get("script", "")
    voice_gen = VoiceGenerator()
    path = voice_gen.generate_for_script(script)
    return jsonify({"audio_path": path})

@app.route("/compose", methods=["POST"])
def compose():
    data = request.get_json() or {}
    scenes = data.get("scenes", [])
    audio = data.get("audio_path", "")
    title = data.get("title", "composed_video")
    composer = VideoComposer()
    path = composer.compose_video(scenes, audio, title)
    return jsonify({"video_path": path})

@app.route("/qc", methods=["POST"])
def quality_control():
    data = request.get_json() or {}
    res = QualityAgent.evaluate_project(
        script=data.get("script", ""),
        scenes=data.get("scenes", []),
        visuals=data.get("visuals", []),
        audio_path=data.get("audio_path", ""),
        video_path=data.get("video_path", "")
    )
    return jsonify(res)

@app.route("/seo", methods=["POST"])
def generate_seo():
    data = request.get_json() or {}
    topic = data.get("topic", "")
    script = data.get("script", "")
    agent = SEOAgent()
    return jsonify(agent.generate_seo(topic, script))

if __name__ == "__main__":
    Config.validate()
    print("[App] Python Worker API server running on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
