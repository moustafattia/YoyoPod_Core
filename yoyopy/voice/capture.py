"""Audio capture backends for local voice interactions."""

from __future__ import annotations

import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Protocol

from loguru import logger

from yoyopy.voice.models import VoiceCaptureRequest, VoiceCaptureResult, VoiceSettings

# VAD tuning constants
_SPEECH_RMS_THRESHOLD = 500      # RMS above this = speech
_SILENCE_RMS_THRESHOLD = 300     # RMS below this = silence
_CHUNK_DURATION_MS = 80          # ms per analysis chunk
_SPEECH_CONFIRM_CHUNKS = 2       # consecutive speech chunks required (filters startup clicks)
_SILENCE_AFTER_SPEECH_MS = 400   # stop after this much silence post-speech
_PRE_SPEECH_TIMEOUT_MS = 3500    # give up if no speech within this window
_HARD_TIMEOUT_EXTRA_S = 1        # extra seconds on top of request timeout


def _rms(chunk: bytes) -> float:
    """Return the RMS amplitude of a 16-bit mono PCM chunk."""
    n = len(chunk) // 2
    if n == 0:
        return 0.0
    samples = struct.unpack(f"<{n}h", chunk[:n * 2])
    return math.sqrt(sum(s * s for s in samples) / n)


class AudioCaptureBackend(Protocol):
    """Backend capable of recording one local audio clip."""

    def is_available(self, settings: VoiceSettings) -> bool:
        """Return True when recording is available."""

    def capture(self, request: VoiceCaptureRequest, settings: VoiceSettings) -> VoiceCaptureResult:
        """Capture one audio clip and return its path."""


class NullAudioCaptureBackend:
    """No-op audio capture backend used when recording is unavailable."""

    def is_available(self, settings: VoiceSettings) -> bool:
        return bool(settings.stt_enabled) and not settings.mic_muted

    def capture(self, request: VoiceCaptureRequest, settings: VoiceSettings) -> VoiceCaptureResult:
        return VoiceCaptureResult(audio_path=request.audio_path, recorded=False)


class SubprocessAudioCaptureBackend:
    """Record a WAV clip via arecord with VAD-based early stop."""

    def __init__(self, *, arecord_binary: str = "arecord") -> None:
        self.arecord_binary = arecord_binary
        self._preferred_device: str | None = None

    def is_available(self, settings: VoiceSettings) -> bool:
        if not settings.stt_enabled or settings.mic_muted:
            return False
        return shutil.which(self.arecord_binary) is not None

    def capture(self, request: VoiceCaptureRequest, settings: VoiceSettings) -> VoiceCaptureResult:
        if request.audio_path is not None:
            return VoiceCaptureResult(audio_path=request.audio_path, recorded=False)
        if not self.is_available(settings):
            return VoiceCaptureResult(audio_path=None, recorded=False)

        with tempfile.NamedTemporaryFile(prefix="yoyopy-voice-", suffix=".wav", delete=False) as handle:
            audio_path = Path(handle.name)

        max_seconds = float(request.timeout_seconds or settings.record_seconds)

        for device in self._device_candidates():
            try:
                recorded = self._capture_vad(
                    audio_path=audio_path,
                    device=device,
                    sample_rate_hz=settings.sample_rate_hz,
                    max_seconds=max_seconds,
                )
            except Exception as exc:
                logger.warning("VAD capture failed on device {}: {}", device, exc)
                continue

            if recorded:
                self._preferred_device = device
                return VoiceCaptureResult(audio_path=audio_path, recorded=True)

        logger.warning("Voice capture failed: no usable ALSA capture device found")
        audio_path.unlink(missing_ok=True)
        return VoiceCaptureResult(audio_path=None, recorded=False)

    def _capture_vad(
        self,
        *,
        audio_path: Path,
        device: str | None,
        sample_rate_hz: int,
        max_seconds: float,
    ) -> bool:
        """Stream raw PCM from arecord, stop on silence after speech, write WAV.

        Returns True if audio was captured successfully.
        """
        chunk_frames = int(sample_rate_hz * _CHUNK_DURATION_MS / 1000)
        chunk_bytes = chunk_frames * 2  # 16-bit mono

        silence_chunks_needed = math.ceil(_SILENCE_AFTER_SPEECH_MS / _CHUNK_DURATION_MS)
        pre_speech_chunks_max = math.ceil(_PRE_SPEECH_TIMEOUT_MS / _CHUNK_DURATION_MS)
        hard_max_chunks = math.ceil(max_seconds * 1000 / _CHUNK_DURATION_MS)

        command = [self.arecord_binary, "-t", "raw", "-f", "S16_LE",
                   "-r", str(sample_rate_hz), "-c", "1", "-q"]
        if device:
            command.extend(["-D", device])
        command.append("-")

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        frames = bytearray()
        speech_detected = False
        speech_run = 0    # consecutive loud chunks (filters startup click)
        silence_run = 0
        pre_speech_chunk_count = 0

        try:
            for _chunk_idx in range(hard_max_chunks + pre_speech_chunks_max):
                raw = proc.stdout.read(chunk_bytes)  # type: ignore[union-attr]
                if not raw:
                    break
                frames.extend(raw)
                rms = _rms(raw)

                if not speech_detected:
                    if rms >= _SPEECH_RMS_THRESHOLD:
                        speech_run += 1
                        if speech_run >= _SPEECH_CONFIRM_CHUNKS:
                            speech_detected = True
                            silence_run = 0
                    else:
                        speech_run = 0
                        pre_speech_chunk_count += 1
                        if pre_speech_chunk_count >= pre_speech_chunks_max:
                            # No confirmed speech in the pre-speech window.
                            break
                else:
                    if rms < _SILENCE_RMS_THRESHOLD:
                        silence_run += 1
                        if silence_run >= silence_chunks_needed:
                            break
                    else:
                        silence_run = 0
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()

        if proc.returncode not in (0, -15, None) and not frames:
            return False

        if not frames:
            return False

        with wave.open(str(audio_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate_hz)
            wf.writeframes(bytes(frames))

        return True

    def _device_candidates(self) -> list[str | None]:
        """Return capture-device candidates, prioritizing any known-good device."""

        # Skip the slow arecord -L scan if we already know a working device.
        if self._preferred_device is not None:
            return [self._preferred_device]

        try:
            result = subprocess.run(
                [self.arecord_binary, "-L"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return self._unique_devices([None, "default", "sysdefault"])

        if result.returncode != 0:
            return self._unique_devices([None, "default", "sysdefault"])

        parsed_devices: list[str] = []
        for line in result.stdout.splitlines():
            device = line.strip()
            if not device or device.startswith(" "):
                continue
            if device in {"null", "default", "sysdefault"}:
                continue
            if device.startswith(
                (
                    "plughw:",
                    "hw:",
                    "default:CARD=",
                    "sysdefault:CARD=",
                    "front:CARD=",
                    "dsnoop:CARD=",
                )
            ):
                parsed_devices.append(device)
        candidates: list[str | None] = [*parsed_devices, None, "default", "sysdefault"]
        return self._unique_devices(candidates)

    @staticmethod
    def _unique_devices(devices: list[str | None]) -> list[str | None]:
        """Preserve device order while removing duplicates."""

        unique: list[str | None] = []
        seen: set[str | None] = set()
        for device in devices:
            if device not in seen:
                seen.add(device)
                unique.append(device)
        return unique
