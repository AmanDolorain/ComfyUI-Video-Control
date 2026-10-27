# Video Control

**Author: Aman · Version: 1.0.7 · ComfyUI custom node**

One control node for video duration, FPS, resolution, an empty video latent, and planned VHS video metadata. Set the timing once and connect its outputs across your workflow.

[Publish on GitHub](GITHUB_SETUP.md) · [Custom node development guide](DEVELOPMENT.md)

## Features

- Duration in seconds, shared FPS and resolution.
- Frame count rounded to the required `4n + 1` layout.
- Empty 16-channel video latent with spatial compression 8 and temporal compression 4.
- `VHS_VIDEOINFO` metadata without saving and reopening an intermediate video.
- Actual duration output for an audio generator's duration input.
- No model downloads, network calls or extra Python packages.

## Compatibility

This is **not a universal latent generator**. Your model must accept a tensor shaped `[1, 16, (frames-1)/4+1, height/8, width/8]`. Matching the LATENT socket alone does not prove model compatibility. The current node supports one video per run and whole-number FPS only. Width and height must be multiples of 16.

Metadata describes the planned clip. If downstream nodes change frame count, resolution or FPS, that metadata must be updated. This node does not generate speech, force TTS duration, mix audio, or perform lip sync.

## Install

Extract the ZIP so that `ComfyUI/custom_nodes/VideoControl/__init__.py` exists, then restart ComfyUI. Search for **Video Control** under **Video / Control**.

Once a GitHub repository is published, install its real repository URL through your Manager's Git URL installation option, or clone it into `ComfyUI/custom_nodes`. Do not install a second copy alongside the extracted version.

Requires Python 3.10+ and ComfyUI's existing PyTorch installation. VHS and your audio/lip-sync nodes are separate workflow dependencies.

## Connections

| Output | Destination |
| --- | --- |
| `latent` | Your compatible sampler's latent input |
| `video_info` | Lip-sync node's `VHS_VIDEOINFO` input, if exposed |
| `frame_count` | A node explicitly requesting an INT frame count, if needed |
| `fps` | Final video creator's FPS / frame_rate FLOAT input |
| `actual_duration_seconds` | Audio generator's duration FLOAT input |
| `width`, `height` | Any other resolution controls that must match |
| `summary` | Preview / display text node |

Convert a destination widget to an input when needed. Do not connect `video_info` to a numeric socket or `latent` directly to an IMAGE socket. Decode the sampler's result with your compatible VAE before sending images to the final video creator. Keep the final video creator and audio mixer.

## Timing example

At 25 FPS, 5 seconds becomes 125 frames and exactly 5 seconds. At 24 FPS, nearest rounding gives 121 frames and approximately 5.041667 seconds. Use **actual_duration_seconds** downstream.

`nearest` chooses the closest valid frame count (ties upward); `at_least` rounds up; `at_most` rounds down. Minimum is one frame; very short requests can therefore exceed the requested duration.

## Development and validation

- `__init__.py`: ComfyUI controls, output types, tensor allocation and node registration.
- `calculations.py`: timing, validation and metadata calculations.
- `tests/test_node.py`: calculation checks and a mocked ComfyUI/PyTorch contract test.

Run `python -m unittest discover -s tests -v` from this folder. These tests do not run real PyTorch allocation, model generation, or a complete ComfyUI workflow. A real workflow test is still required.

## License

MIT. See [LICENSE](LICENSE).
