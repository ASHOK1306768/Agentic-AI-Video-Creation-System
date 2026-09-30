import re
from typing import List, Dict

class SceneExtractor:
    @staticmethod
    def extract_scenes(script: str) -> List[Dict]:
        """
        Divide the script into individual scenes using [SCENE BREAK] or sentence boundaries.
        Returns a list of structured scene objects compatible with both n8n and Python pipelines.
        """
        # Split by marker or newlines
        if "[SCENE BREAK]" in script:
            raw_scenes = script.split("[SCENE BREAK]")
        else:
            raw_scenes = [s for s in script.split("\n\n") if s.strip()]

        extracted_scenes = []
        scene_counter = 1

        for raw_scene in raw_scenes:
            scene_text = raw_scene.strip().replace("\n", " ")
            if len(scene_text) > 5:
                duration = SceneExtractor._estimate_duration(scene_text)
                clean_description = scene_text[:120].strip()

                # Extract relevant keywords for image/stock video search
                stop_words = {
                    "what", "if", "could", "completely", "change", "the", "way", "you", 
                    "learn", "today", "is", "helping", "and", "in", "a", "more", "with",
                    "this", "that", "from", "have", "they", "will", "your", "for", "are"
                }
                tokens = re.findall(r'\b[a-zA-Z]{3,}\b', scene_text.lower())
                filtered_keywords = [w for w in tokens if w not in stop_words]
                search_query = " ".join(filtered_keywords[:4]) if filtered_keywords else "technology innovation"

                extracted_scenes.append({
                    "scene_id": scene_counter,
                    "scene_number": scene_counter,
                    "text": scene_text,
                    "narration": scene_text,
                    "duration_seconds": duration,
                    "visual_description": clean_description,
                    "search_keywords": search_query,
                    "word_count": len(scene_text.split())
                })
                scene_counter += 1

        return extracted_scenes

    @staticmethod
    def _estimate_duration(text: str) -> int:
        """
        Estimates speech duration in seconds based on ~140 words per minute.
        Ensures a minimum display time of 4 seconds per scene.
        """
        words = len(text.split())
        duration_seconds = max(int((words / 140.0) * 60), 4)
        return duration_seconds

if __name__ == "__main__":
    test_script = "What if AI could change learning?\n[SCENE BREAK]\nAI tutors give personalized instant feedback.\n[SCENE BREAK]\nAre you ready for the future?"
    scenes = SceneExtractor.extract_scenes(test_script)
    print(f"Extracted {len(scenes)} scenes:")
    for s in scenes:
        print(s)
