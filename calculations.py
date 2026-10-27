"""Pure calculations: intentionally independent of ComfyUI and PyTorch."""
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class VideoPlan:
    width: int
    height: int
    fps: float
    requested_seconds: float
    frame_count: int
    actual_seconds: float
    latent_shape: tuple

    def video_info(self):
        # VHS and lvqunx LatentSync expect these exact dictionary keys.
        values = dict(fps=self.fps, frame_count=self.frame_count,
                      duration=self.actual_seconds, width=self.width, height=self.height)
        return {f'{prefix}_{key}': value
                for prefix in ('source', 'loaded') for key, value in values.items()}

    def summary(self):
        return (f'16-channel video format | {self.width}x{self.height} | {self.fps:g} FPS\n'
                f'Requested: {self.requested_seconds:g}s | Frames: {self.frame_count}\n'
                f'Actual duration: {self.actual_seconds:.6f}s | '
                f'Difference: {self.actual_seconds-self.requested_seconds:+.6f}s\n'
                f'Latent shape: {self.latent_shape}\n'
                'Planned metadata, not a measurement of post-processed frames.')

def make_plan(duration_seconds, fps, width, height, rounding='nearest', batch_size=1):
    seconds, rate = float(duration_seconds), float(fps)
    if not math.isfinite(seconds) or not 0.01 <= seconds <= 600:
        raise ValueError('Duration must be finite and between 0.01 and 600 seconds.')
    if not math.isfinite(rate) or not 1 <= rate <= 120 or not rate.is_integer():
        raise ValueError('Use a whole-number FPS from 1 to 120: this LatentSync wrapper rounds FPS.')
    if batch_size != 1:
        raise ValueError('Use batch_size=1. This workflow carries metadata for one video, not multiple clips.')
    for name, number in (('width', width), ('height', height)):
        if isinstance(number, bool) or not isinstance(number, int) or not 16 <= number <= 16384 or number % 16:
            raise ValueError(f'{name} must be a multiple of 16, between 16 and 16384.')
    target = seconds * rate
    index = (target - 1) / 4
    if rounding == 'nearest':
        groups = math.floor(index + 0.5)
    elif rounding == 'at_least':
        groups = math.ceil(index - 1e-10)
    elif rounding == 'at_most':
        groups = math.floor(index + 1e-10)
    else:
        raise ValueError('Unknown frame rounding mode.')
    frames = max(0, groups) * 4 + 1
    if frames > 16381:
        raise ValueError('Calculated frame count exceeds 16381. Reduce duration or FPS.')
    shape = (1, 16, (frames-1)//4+1, height//8, width//8)
    return VideoPlan(width, height, rate, seconds, frames, frames/rate, shape)
