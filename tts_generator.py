import asyncio
import edge_tts
from config import TTS_VOICE


async def _synthesise(text: str, output_path: str, voice: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_audio(text: str, output_path: str, voice: str = TTS_VOICE) -> None:
    """
    Convert text to speech and save as an MP3 file.
    Uses Microsoft Edge TTS — free, no API key required.
    """
    # asyncio.run works on Windows with Python 3.10+
    asyncio.run(_synthesise(text, output_path, voice))


def list_voices() -> None:
    """Helper: print all available edge-tts voices."""
    async def _list():
        voices = await edge_tts.list_voices()
        for v in voices:
            print(v["ShortName"], "-", v["Locale"])
    asyncio.run(_list())


if __name__ == "__main__":
    # Quick test
    generate_audio("Hello! This is a test of the text to speech system.", "test_audio.mp3")
    print("Saved test_audio.mp3")
