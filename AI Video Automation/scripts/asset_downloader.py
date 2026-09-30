import requests
from config import Config
from pathlib import Path
from typing import List, Dict, Optional
import time
import os
from PIL import Image, ImageDraw, ImageFont

class AssetDownloader:
    def __init__(self):
        self.pexels_key = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY
        self.assets_dir = Config.ASSETS_DIR
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def download_images_for_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Download or generate visual assets for each scene.
        Guarantees that every scene receives a valid 9:16 vertical image file.
        """
        downloaded_assets = []

        for scene in scenes:
            scene_id = scene.get("scene_number", scene.get("scene_id", 1))
            query = scene.get("search_keywords", scene.get("visual_description", "technology"))
            target_filename = f"scene_{scene_id:02d}.jpg"
            target_path = self.assets_dir / target_filename

            # If already downloaded, reuse
            if target_path.exists() and target_path.stat().st_size > 1000:
                downloaded_assets.append({
                    "scene_id": scene_id,
                    "images": [str(target_path)],
                    "status": "success",
                    "source": "cache"
                })
                continue

            print(f"[AssetDownloader] Fetching asset for scene {scene_id}: '{query}'")
            success = False

            # 1. Try Pexels
            if self.pexels_key and not success:
                try:
                    photos = self._search_pexels(query, per_page=3)
                    if photos:
                        image_url = photos[0]["src"].get("portrait", photos[0]["src"].get("large"))
                        self._download_image(image_url, target_path)
                        success = True
                        source = "pexels"
                        time.sleep(0.5) # Rate limiting
                except Exception as e:
                    print(f"[AssetDownloader] Pexels search failed: {e}")

            # 2. Try Pixabay
            if self.pixabay_key and not success:
                try:
                    hits = self._search_pixabay(query, per_page=3)
                    if hits:
                        image_url = hits[0].get("largeImageURL", hits[0].get("webformatURL"))
                        self._download_image(image_url, target_path)
                        success = True
                        source = "pixabay"
                        time.sleep(0.5)
                except Exception as e:
                    print(f"[AssetDownloader] Pixabay search failed: {e}")

            # 3. Fallback: High Quality Procedural Vertical 9:16 Graphic
            if not success:
                print(f"[AssetDownloader] Creating procedural vertical visual for Scene {scene_id}...")
                self._generate_procedural_image(scene, target_path)
                source = "procedural_generator"

            downloaded_assets.append({
                "scene_id": scene_id,
                "images": [str(target_path)],
                "status": "success",
                "source": source
            })

        return downloaded_assets

    def _search_pexels(self, query: str, per_page: int = 5) -> List[Dict]:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": per_page, "orientation": "portrait"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("photos", [])
        return []

    def _search_pixabay(self, query: str, per_page: int = 5) -> List[Dict]:
        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_key,
            "q": query,
            "image_type": "photo",
            "orientation": "vertical",
            "per_page": per_page
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("hits", [])
        return []

    def _download_image(self, url: str, output_path: Path):
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)

    def _generate_procedural_image(self, scene: Dict, output_path: Path):
        """Creates a vibrant 1080x1920 vertical background card if no stock API key is set."""
        width, height = Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT
        
        # Select background gradient colors based on scene number
        color_palettes = [
            ((15, 23, 42), (30, 58, 138)),    # Deep blue
            ((15, 23, 42), (88, 28, 135)),    # Dark violet
            ((17, 24, 39), (4, 120, 87)),     # Emerald
            ((30, 41, 59), (180, 83, 9)),     # Amber
            ((24, 24, 27), (190, 24, 93))     # Rose
        ]
        scene_num = scene.get("scene_number", 1)
        c1, c2 = color_palettes[(scene_num - 1) % len(color_palettes)]

        # Generate vertical gradient
        img = Image.new("RGB", (width, height), c1)
        draw = ImageDraw.Draw(img)
        for y in range(height):
            ratio = y / height
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Decorative visual card elements
        draw.rectangle([80, 200, width - 80, height - 300], outline=(255, 255, 255, 60), width=3)
        draw.rectangle([100, 220, width - 100, 300], fill=(255, 255, 255, 20))
        
        # Text annotations
        draw.text((120, 245), f"SCENE {scene_num}", fill=(255, 255, 255))
        keywords = scene.get("search_keywords", "").upper()
        draw.text((120, 340), f"Topic: {keywords}", fill=(200, 225, 255))

        img.save(output_path, "JPEG", quality=90)

if __name__ == "__main__":
    test_scenes = [
        {"scene_number": 1, "search_keywords": "artificial intelligence", "visual_description": "AI learning"},
        {"scene_number": 2, "search_keywords": "students studying technology", "visual_description": "online class"}
    ]
    downloader = AssetDownloader()
    res = downloader.download_images_for_scenes(test_scenes)
    print("Downloaded assets:", res)
