import os
import sys
from pathlib import Path

# Ensure safe printing on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add scripts directory to sys.path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from config import Config
from script_generator import ScriptGenerator
from scene_extractor import SceneExtractor
from asset_downloader import AssetDownloader
from voice_generator import VoiceGenerator
from quality_agent import QualityAgent
from seo_agent import SEOAgent

def run_tests():
    print("=" * 60)
    print("RUNNING AGENTIC AI VIDEO AUTOMATION VERIFICATION SUITE")
    print("=" * 60)

    # 1. Config Test
    print("\n[Step 1/7] Testing Configuration & Directories...")
    Config.validate()
    assert Config.OUTPUT_DIR.exists(), "Output directory missing!"
    print("[OK] Configuration validated successfully.")

    # 2. Script Generator Test
    print("\n[Step 2/7] Testing Script Generation...")
    prompt = "Artificial Intelligence in Education"
    generator = ScriptGenerator()
    script_res = generator.generate(prompt, duration_seconds=30)
    assert script_res["status"] == "success", "Script generation failed!"
    script = script_res["script"]
    print(f"[OK] Script generated successfully ({len(script)} characters).")

    # 3. Scene Extractor Test
    print("\n[Step 3/7] Testing Scene Extraction...")
    scenes = SceneExtractor.extract_scenes(script)
    assert len(scenes) > 0, "No scenes extracted!"
    print(f"[OK] Extracted {len(scenes)} scenes:")
    for s in scenes:
        print(f"   Scene {s['scene_number']}: {s['narration'][:50]}... ({s['duration_seconds']}s)")

    # 4. Asset Downloader Test
    print("\n[Step 4/7] Testing Asset Downloader (Pexels/Pixabay/Procedural)...")
    downloader = AssetDownloader()
    visuals = downloader.download_images_for_scenes(scenes)
    assert len(visuals) == len(scenes), "Visual count mismatch!"
    for v in visuals:
        assert Path(v["images"][0]).exists(), f"Image not created: {v['images'][0]}"
    print(f"[OK] Successfully prepared {len(visuals)} visual scenes.")

    # 5. Voice Generator Test
    print("\n[Step 5/7] Testing Voiceover Audio Generation (TTS)...")
    voice_gen = VoiceGenerator()
    audio_path = voice_gen.generate_for_script(scenes[0]["narration"], filename="test_voiceover.mp3")
    assert Path(audio_path).exists() or Path(audio_path).with_suffix(".wav").exists(), "Audio file not created!"
    print(f"[OK] Audio voice-over created: {audio_path}")

    # 6. SEO Agent Test
    print("\n[Step 6/7] Testing SEO Metadata Generation (YT Shorts & IG Reels)...")
    seo_agent = SEOAgent()
    seo_data = seo_agent.generate_seo(prompt, script)
    assert "youtube_title" in seo_data, "Missing youtube_title in SEO output!"
    assert "instagram_caption" in seo_data, "Missing instagram_caption in SEO output!"
    print(f"[OK] YouTube Title: {seo_data['youtube_title']}")
    print(f"[OK] Instagram Caption: {seo_data['instagram_caption']}")

    # 7. Quality Control Agent Test
    print("\n[Step 7/7] Testing Quality Control Agent...")
    qc = QualityAgent.evaluate_project(
        script=script,
        scenes=scenes,
        visuals=visuals,
        audio_path=audio_path,
        video_path="outputs/videos/placeholder.mp4"
    )
    print(f"[OK] QC Status: {qc['status']}, Score: {qc['quality_score']}")
    print("   Files checked:", qc["files_checked"])

    print("\n" + "=" * 60)
    print("ALL AGENTIC AI AUTOMATION MODULE TESTS PASSED! [SUCCESS]")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
