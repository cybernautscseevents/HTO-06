import io
import subprocess
import tempfile
import wave

import speech_recognition as sr
import imageio_ffmpeg


# ---------------------------------------------------------
# AUDIO CONVERTER
# ---------------------------------------------------------

def convert_to_wav(audio_data: bytes) -> bytes:
    """
    Convert uploaded audio into WAV format.

    Supports formats such as:
    AAC, M4A, MP3, WAV, etc.

    FFmpeg runs locally.
    No paid API is used here.
    """

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.NamedTemporaryFile(
        suffix=".input",
        delete=False
    ) as input_file:

        input_path = input_file.name
        input_file.write(audio_data)

    output_path = input_path + ".wav"

    try:

        command = [
            ffmpeg_path,
            "-y",
            "-i",
            input_path,
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            output_path
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        with open(output_path, "rb") as wav_file:
            return wav_file.read()

    finally:

        import os

        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)


# ---------------------------------------------------------
# SPEECH TO TEXT
# ---------------------------------------------------------

def transcribe_audio(
    audio_data: bytes,
    language: str = "en-IN"
) -> str:
    """
    Convert speech audio into text.

    language:
        en-IN = English India
        kn-IN = Kannada India
    """

    recognizer = sr.Recognizer()

    try:

        # Convert any supported audio format to WAV
        wav_data = convert_to_wav(audio_data)

        # Read WAV data
        audio_stream = io.BytesIO(wav_data)

        with wave.open(audio_stream, "rb") as wav_file:

            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            frames = wav_file.readframes(
                wav_file.getnframes()
            )

        audio = sr.AudioData(
            frames,
            sample_rate,
            sample_width
        )

        # Speech-to-text
        text = recognizer.recognize_google(
            audio,
            language=language
        )

        return text.strip()

    except sr.UnknownValueError:

        return ""

    except sr.RequestError as error:

        raise RuntimeError(
            f"Speech recognition service error: {error}"
        )

    except subprocess.CalledProcessError:

        raise RuntimeError(
            "Could not convert the uploaded audio file."
        )

    except Exception as error:

        raise RuntimeError(
            f"Audio processing error: {error}"
        )