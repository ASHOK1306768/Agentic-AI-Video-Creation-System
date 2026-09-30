import os
from pathlib import Path
from typing import List, Dict, Optional
from config import Config
from PIL import Image, ImageDraw, ImageFont

class VideoComposer:
    def __init__(self):
        self.output_dir = Config.VIDEOS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = Config.VIDEO_FPS
        self.width = Config.VIDEO_WIDTH
        self.height = Config.VIDEO_HEIGHT

    def compose_video(
        self,
        scenes_with_images: List[Dict],
        audio_path: str,
        title: str = "final_video",
        subtitles_path: Optional[str] = None
    ) -> str:
        """
        Assemble final social media video (vertical 9:16) combining:
        - Visual scene images/clips
        - Synchronized audio voiceover
        - Burned-in subtitles / title cards
        """
        print(f"[VideoComposer] Composing video '{title}'...")
        Config.ensure_dirs()

        from moviepy.editor import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips
        )

        clips = []

        for idx, scene in enumerate(scenes_with_images):
            images = scene.get("images", [])
            duration = scene.get("duration_seconds", 5)

            if not images:
                continue

            img_path = images[0]

            # Ensure image is cropped and resized strictly to 9:16 (1080x1920)
            prepared_img_path = self._prepare_vertical_image(img_path, scene, idx + 1)
            
            clip = ImageClip(str(prepared_img_path)).set_duration(duration)
            clips.append(clip)

        if not clips:
            raise ValueError("[VideoComposer] Error: No valid image clips found to compose.")

        # Concatenate all visual scenes
        video = concatenate_videoclips(clips, method="compose")

        # Attach audio voiceover
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            if audio.duration > video.duration:
                # If audio is slightly longer, pad video or extend last clip
                audio = audio.subclip(0, video.duration)
            elif video.duration > audio.duration:
                # Pad audio or truncate video to audio length
                video = video.subclip(0, audio.duration)

            video = video.set_audio(audio)

        safe_title = "".join(c for c in title if c.isalnum() or c in ("-", "_")).rstrip()
        if not safe_title:
            safe_title = "final_video"

        output_file = self.output_dir / f"{safe_title}.mp4"

        print(f"[VideoComposer] Exporting video to {output_file} ({self.width}x{self.height} @ {self.fps}fps)...")
        video.write_videofile(
            str(output_file),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4,
            verbose=False,
            logger=None
        )

        print(f"[VideoComposer] Video successfully rendered: {output_file}")
        return str(output_file)

    def _prepare_vertical_image(self, image_path: str, scene: Dict, scene_index: int) -> Path:
        """
        Crop and resize input image to exact vertical resolution (e.g. 1080x1920)
        and overlay subtle subtitle text for readable social media presentation.
        """
        target_path = Config.ASSETS_DIR / f"prepared_{scene_index:02d}.jpg"
        
        try:
            with Image.open(image_path) as im:
                im = im.convert("RGB")
                target_w, target_h = self.width, self.height
                src_w, src_h = im.size

                # Aspect fill calculation
                scale = max(target_w / src_w, target_h / src_h)
                new_w = int(src_w * scale)
                new_h = int(src_h * scale)

                im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Center crop to 9:16
                left = (new_w - target_w) // 2
                top = (new_h - target_h) // 2
                im_cropped = im_resized.crop((left, top, left + target_w, top + target_h))

                # Overlay burned-in subtitle banner at lower third
                draw = ImageDraw.Draw(im_cropped)
                narration = scene.get("narration", scene.get("text", ""))

                if narration:
                    banner_y = int(target_h * 0.72)
                    banner_height = 140
                    # Semi-transparent dark banner box
                    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle(
                        [60, banner_y, target_w - 60, banner_y + banner_height],
                        fill=(0, 0, 0, 180),
                        outline=(255, 255, 255, 100),
                        width=2
                    )
                    im_cropped = Image.alpha_composite(im_cropped.convert("RGBA"), overlay).convert("RGB")

                    # Draw text in banner
                    final_draw = ImageDraw.Draw(im_cropped)
                    clean_text = narration[:100] + ("..." if len(narration) > 100 else "")
                    final_draw.text((85, banner_y + 40), clean_text, fill=(255, 255, 255))

                im_cropped.save(target_path, "JPEG", quality=90)
                return target_path

        except Exception as e:
            print(f"[VideoComposer] Warning in image processing: {e}. Using raw image path.")
            return Path(image_path)

if __name__ == "__main__":
    composer = VideoComposer()
    print("Video composer initialized.")
