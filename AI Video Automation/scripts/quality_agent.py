from pathlib import Path
from typing import Dict, List
from config import Config

class QualityAgent:
    """
    Automated Quality Control Agent (Module 4 / Nodes 20-22 in n8n Manual).
    Verifies completeness, audio-visual integrity, and output format.
    """
    @staticmethod
    def evaluate_project(
        script: str,
        scenes: List[Dict],
        visuals: List[Dict],
        audio_path: str,
        video_path: str,
        subtitles_path: str = ""
    ) -> Dict:
        issues = []
        quality_score = 100

        # 1. Script validation
        if not script or len(script.strip()) < 30:
            issues.append("Script is too short or missing.")
            quality_score -= 25

        # 2. Scenes validation
        if not scenes:
            issues.append("No scenes were extracted.")
            quality_score -= 25
        else:
            for s in scenes:
                if not s.get("narration"):
                    issues.append(f"Scene {s.get('scene_number')} has empty narration.")
                    quality_score -= 10
                if s.get("duration_seconds", 0) <= 0:
                    issues.append(f"Scene {s.get('scene_number')} duration is invalid.")
                    quality_score -= 5

        # 3. Visual assets verification
        if not visuals:
            issues.append("No visual assets found.")
            quality_score -= 25
        else:
            for v in visuals:
                img_list = v.get("images", [])
                if not img_list or not Path(img_list[0]).exists():
                    issues.append(f"Visual for scene {v.get('scene_id')} is missing on disk.")
                    quality_score -= 15

        # 4. Audio voiceover verification
        if not audio_path or not Path(audio_path).exists() or Path(audio_path).stat().st_size < 100:
            issues.append("Voiceover audio file is missing or corrupted.")
            quality_score -= 25

        # 5. Final video verification
        if not video_path or not Path(video_path).exists() or Path(video_path).stat().st_size < 1000:
            issues.append("Final MP4 video was not created.")
            quality_score -= 30

        quality_score = max(quality_score, 0)
        status = "PASS" if quality_score >= 80 and not any("missing" in i for i in issues) else "FAIL"

        return {
            "status": status,
            "quality_score": quality_score,
            "issues": issues,
            "files_checked": {
                "script": bool(script),
                "scenes_count": len(scenes),
                "visuals_count": len(visuals),
                "audio_exists": bool(audio_path and Path(audio_path).exists()),
                "video_exists": bool(video_path and Path(video_path).exists())
            }
        }

if __name__ == "__main__":
    result = QualityAgent.evaluate_project("Sample script text...", [], [], "", "")
    print(result)
