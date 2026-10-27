"""Pure calculations: intentionally independent of ComfyUI and PyTorch."""
import math
from dataclasses import dataclass

RESOLUTION_PRESETS = {
    'Custom': None,
    'Tiny 64 x 64': (64, 64),
    'Small 128 x 128': (128, 128),
    'Small 256 x 256': (256, 256),
    '360p 640 x 360': (640, 360),
    '480p 848 x 480': (848, 480),
    'Square 512 x 512': (512, 512),
    '720p 1280 x 720': (1280, 720),
    'Portrait 720 x 1280': (720, 1280),
    '1080p 1920 x 1080': (1920, 1080),
    'Portrait 1080 x 1920': (1080, 1920),
    '1440p 2560 x 1440': (2560, 1440),
    '4K UHD 3840 x 2160': (3840, 2160),
    'Portrait 4K 2160 x 3840': (2160, 3840),
    '4K DCI 4096 x 2160': (4096, 2160),
}


def resolve_resolution(width, height, resolution_preset='Custom', size_rounding='nearest'):
    """Accept pixel-by-pixel custom input; align only the generated latent size."""
    if resolution_preset not in RESOLUTION_PRESETS:
        raise ValueError('Unknown resolution preset.')
    if size_rounding not in ('nearest', 'down', 'up', 'exact'):
        raise ValueError('Unknown size rounding mode.')
    preset = RESOLUTION_PRESETS[resolution_preset]
    requested = preset if preset is not None else (width, height)
    actual = []
    for name, number in zip(('width', 'height'), requested):
        if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= 16384:
            raise ValueError(f'{name} must be a whole number between 1 and 16384.')
        if size_rounding == 'exact':
            if number % 16:
                raise ValueError(f'Exact size {name}={number} is not supported by this latent format. '
                                 'Choose nearest, down or up to align it automatically.')
            aligned = number
        elif size_rounding == 'nearest':
            aligned = ((number + 8) // 16) * 16
        elif size_rounding == 'down':
            aligned = (number // 16) * 16
        else:
            aligned = ((number + 15) // 16) * 16
        # A zero-sized latent is invalid; all automatic modes have a 16px minimum.
        actual.append(max(16, aligned))
    return (*requested, *actual)

@dataclass(frozen=True)
class VideoPlan:
    width: int
    height: int
    fps: float
    requested_seconds: float
    frame_count: int
    actual_seconds: float
    latent_shape: tuple
    requested_width: int
    requested_height: int
    size_rounding: str
    resolution_preset: str

    def video_info(self):
        # VHS and lvqunx LatentSync expect these exact dictionary keys.
        values = dict(fps=self.fps, frame_count=self.frame_count,
                      duration=self.actual_seconds, width=self.width, height=self.height)
        return {f'{prefix}_{key}': value
                for prefix in ('source', 'loaded') for key, value in values.items()}

    def summary(self):
        return (f'16-channel video format | {self.width}x{self.height} | {self.fps:g} FPS\n'
                f'Requested size: {self.requested_width}x{self.requested_height} | '
                f'Actual size: {self.width}x{self.height} | Size mode: {self.size_rounding}\n'
                f'Resolution preset: {self.resolution_preset}\n'
                f'Requested: {self.requested_seconds:g}s | Frames: {self.frame_count}\n'
                f'Actual duration: {self.actual_seconds:.6f}s | '
                f'Difference: {self.actual_seconds-self.requested_seconds:+.6f}s\n'
                f'Latent shape: {self.latent_shape}\n'
                'Planned metadata, not a measurement of post-processed frames.')

def make_plan(duration_seconds, fps, width, height, rounding='nearest', batch_size=1,
              resolution_preset='Custom', size_rounding='nearest'):
    seconds, rate = float(duration_seconds), float(fps)
    if not math.isfinite(seconds) or not 0.01 <= seconds <= 600:
        raise ValueError('Duration must be finite and between 0.01 and 600 seconds.')
    if not math.isfinite(rate) or not 1 <= rate <= 120 or not rate.is_integer():
        raise ValueError('Use a whole-number FPS from 1 to 120: this LatentSync wrapper rounds FPS.')
    if batch_size != 1:
        raise ValueError('Use batch_size=1. This workflow carries metadata for one video, not multiple clips.')
    requested_width, requested_height, width, height = resolve_resolution(
        width, height, resolution_preset, size_rounding)
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
    return VideoPlan(width, height, rate, seconds, frames, frames/rate, shape,
                     requested_width, requested_height, size_rounding, resolution_preset)
