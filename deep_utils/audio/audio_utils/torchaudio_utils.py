import math
from pathlib import Path
from typing import Union, List

import torch
import torchaudio
from torchaudio import transforms as T

from deep_utils.utils.logging_utils import log_print
from deep_utils.utils.os_utils.os_path import split_extension


class TorchAudioUtils:
    @staticmethod
    def resample(
            wave: Union[str, Path, torch.Tensor],
            sr: int = None,
            resample_rate=16000,
            save=False,
            resampled_path: str = None,
            logger=None,
    ) -> Union[str, torch.Tensor]:
        """
        This file is used to resample an audio file or torch tensor
        :param wave:
        :param sr:
        :param resample_rate:
        :param save:
        :param resampled_path:
        :param logger:
        :return:
        """

        if isinstance(wave, str) or isinstance(wave, Path):
            waveform, sample_rate = torchaudio.load(wave)
            if save:
                wave_path = (
                    split_extension(wave, suffix=f"_{resample_rate}")
                    if resampled_path is None
                    else resampled_path
                )
        else:
            waveform = wave
            sample_rate = sr
            if save:
                wave_path = resampled_path

        resampler = T.Resample(
            sample_rate, resample_rate, dtype=waveform.dtype)
        resampled_waveform = resampler(waveform)
        if save:
            torchaudio.save(
                wave_path,
                resampled_waveform,
                resample_rate,
                encoding="PCM_S",
                bits_per_sample=16,
            )
            log_print(
                logger,
                f"Successfully resampled and saved wav-file to {wave_path} with {resample_rate} sample rate!",
            )
            return wave_path
        else:
            log_print(
                logger,
                f"Successfully resampled wav-file {waveform.shape} with {resample_rate} sample rate!",
            )
            return resampled_waveform

    @staticmethod
    def split(
            wave, sr, max_seconds: float = 10, min_seconds=1, logger=None, verbose=1
    ) -> List[torch.Tensor]:
        """
        Splits a wave to mini-waves based on input max_seconds. If the last segment's duration is less than min_seconds
        it is combined with its previous segment.
        :param wave:
        :param sr:
        :param max_seconds:
        :param min_seconds:
        :param logger:
        :param verbose:
        :return:
        """
        wave_duration = TorchAudioUtils.get_duration(wave, sr)
        if max_seconds is None or wave_duration < max_seconds:
            return [wave]

        unsqueeze = False
        if len(wave.shape) == 2:
            wave = wave.squeeze(0)
            unsqueeze = True
        n_intervals = math.ceil(wave_duration / max_seconds)
        waves = []

        for interval in range(n_intervals):
            s = (interval * max_seconds) * sr
            e = ((interval + 1) * max_seconds) * sr
            w = wave[s:e]
            w_duration = TorchAudioUtils.get_duration(w, sr)
            w = w.unsqueeze(0) if unsqueeze else w
            if w_duration < min_seconds:
                waves[-1] = torch.concat([waves[-1], w], dim=1)
            else:
                waves.append(w)
        if len(waves) > 1:
            log_print(
                logger,
                f"Successfully split input wave to {len(waves)} waves!",
                verbose=verbose,
            )
        return waves

    @staticmethod
    def get_duration(wave, sr):
        """
        Computing the duration of a wav array
        :param wave:
        :param sr:
        :return: duration in seconds
        """
        if len(wave.shape) == 2:
            wave = wave.squeeze(0)
        return wave.shape[0] / sr

    @staticmethod
    def get_file_duration(wav_path: Union[Path, str]):
        """
        Computing the duration of a wav file
        :param wav_path:
        :return: duration in seconds
        """
        speech_array, sampling_rate = torchaudio.load(wav_path)
        duration_in_seconds = speech_array.shape[1] / sampling_rate
        return duration_in_seconds
