import io
import os
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
    Convert browser WebM audio directly into
    mono 16 kHz 16-bit WAV.

    The WAV output is kept in memory.
    """

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False
    ) as input_file:

        input_path = input_file.name
        input_file.write(audio_data)

    try:

        command = [
            ffmpeg_path,

            "-loglevel",
            "error",

            "-i",
            input_path,

            # Speech recognition does not need stereo.
            "-ac",
            "1",

            # 16 kHz is enough for speech recognition.
            "-ar",
            "16000",

            # 16-bit PCM WAV.
            "-acodec",
            "pcm_s16le",

            # Write WAV to stdout instead of creating
            # another temporary file.
            "-f",
            "wav",

            "pipe:1",
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        return result.stdout

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)


# ---------------------------------------------------------
# SPEECH TO TEXT
# ---------------------------------------------------------

def transcribe_audio(
    audio_data: bytes,
    language: str = "en-IN"
) -> str:
    """
    Convert recorded browser audio into text.

    Supported locales:

        en-IN = Indian English; kn-IN = Kannada; ta-IN = Tamil;
        te-IN = Telugu; hi-IN = Hindi; ml-IN = Malayalam.
    """

    recognizer = sr.Recognizer()

    try:

        # -------------------------------------------------
        # Convert WebM -> WAV
        # -------------------------------------------------

        wav_data = convert_to_wav(audio_data)

        # -------------------------------------------------
        # Read WAV directly from memory
        # -------------------------------------------------

        audio_stream = io.BytesIO(wav_data)

        with wave.open(audio_stream, "rb") as wav_file:

            frames = wav_file.readframes(
                wav_file.getnframes()
            )

            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()

        audio = sr.AudioData(
            frames,
            sample_rate,
            sample_width
        )

        # -------------------------------------------------
        # Google Speech Recognition
        # -------------------------------------------------

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

    except subprocess.CalledProcessError as error:

        raise RuntimeError(
            "Could not convert the uploaded audio file."
        ) from error

    except Exception as error:

        raise RuntimeError(
            f"Audio processing error: {error}"
        )
