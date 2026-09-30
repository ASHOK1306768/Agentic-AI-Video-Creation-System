import os
import asyncio
from config import Config
from pathlib import Path
from typing import Optional

class VoiceGenerator:
    def __init__(self):
        self.output_dir = Config.AUDIO_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.google_creds = Config.GOOGLE_APPLICATION_CREDENTIALS

    def generate_audio(self, text: str, output_file: str = "voiceover.mp3") -> str:
        """
        Convert text script to high quality speech.
        Tries:
        1. Google Cloud Text-to-Speech (Neural2-C) if credentials exist.
        2. Free Edge-TTS neural speech (en-US-ChristopherNeural/en-US-JennyNeural).
        3. Synthetic audio fallback if offline.
        """
        filepath = self.output_dir / output_file
        clean_text = text.replace("[SCENE BREAK]", " ").strip()

        # 1. Try Google Cloud TTS if credential file exists
        if self.google_creds and os.path.exists(self.google_creds):
            try:
                from google.cloud import texttospeech
                client = texttospeech.TextToSpeechClient()
                synthesis_input = texttospeech.SynthesisInput(text=clean_text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Neural2-C"
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.05
                )
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                with open(filepath, "wb") as f:
                    f.write(response.audio_content)
                print(f"[VoiceGenerator] Google Cloud TTS saved: {filepath}")
                return str(filepath)
            except Exception as e:
                print(f"[VoiceGenerator] Google Cloud TTS attempt error: {e}. Falling back to edge-tts.")

        # 2. Try Edge-TTS (Completely free neural TTS, no API key required)
        try:
            import edge_tts
            async def _synthesize():
                communicate = edge_tts.Communicate(clean_text, "en-US-ChristopherNeural")
                await communicate.save(str(filepath))
            
            asyncio.run(_synthesize())
            if filepath.exists() and filepath.stat().st_size > 500:
                print(f"[VoiceGenerator] Edge-TTS voice-over saved: {filepath}")
                return str(filepath)
        except Exception as e:
            print(f"[VoiceGenerator] Edge-TTS error: {e}. Generating procedural audio.")

        # 3. Last fallback: Generate synthetic wav tone file
        actual_path = self._generate_tone_audio(filepath, duration_seconds=max(int(len(clean_text.split()) / 2.5), 5))
        return str(actual_path)

    def _generate_tone_audio(self, filepath: Path, duration_seconds: int = 10):
        """Generates a soft synthetic audio placeholder using scipy/wave."""
        import wave
        import math
        import struct

        sample_rate = 44100
        num_samples = sample_rate * duration_seconds
        wav_path = filepath.with_suffix(".wav")

        with wave.open(str(wav_path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(num_samples):
                # Gentle 440 Hz tone with envelope
                t = float(i) / sample_rate
                val = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * 440.0 * t))
                data = struct.pack("<h", val)
                wav_file.writeframesraw(data)

        print(f"[VoiceGenerator] Synthetic fallback audio generated: {wav_path}")
        return str(wav_path)

    def generate_for_script(self, script: str, filename: str = "voiceover.mp3") -> str:
        print("[VoiceGenerator] Generating voice-over narration...")
        return self.generate_audio(script, filename)

if __name__ == "__main__":
    vg = VoiceGenerator()
    path = vg.generate_for_script("What if AI could change the way you learn?")
    print("Voice-over saved at:", path)
