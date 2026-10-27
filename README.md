# ComfyUI-Video-Control

**Author: Aman · Version: 1.1.5 · ComfyUI custom node**

One control node for video duration, FPS, resolution, an empty video latent, and planned VHS video metadata. Set the timing once and connect its outputs across your workflow.

[Registry publishing](REGISTRY_SETUP.md) · [Publish on GitHub](GITHUB_SETUP.md) · [Custom node development guide](DEVELOPMENT.md)

## Features

- Duration in seconds, shared FPS and resolution.
- Pixel-by-pixel custom resolution entry with automatic size rounding.
- Tiny, square, landscape and portrait presets through UHD/DCI 4K.
- Frame count rounded to the required `4n + 1` layout.
- Empty 16-channel video latent with spatial compression 8 and temporal compression 4.
- `VHS_VIDEOINFO` metadata without saving and reopening an intermediate video.
- Actual duration output for an audio generator's duration input.
- No model downloads, network calls or extra Python packages.
- Small `Author: Aman` credit anchored to the bottom-right footer, with attribution in the description.

## Compatibility

This is **not a universal latent generator**. Your model must accept a tensor shaped `[1, 16, (frames-1)/4+1, height/8, width/8]`. Matching the LATENT socket alone does not prove model compatibility. The current node supports one video per run and whole-number FPS only. Custom width and height accept any whole number from 1 to 16384. Automatic modes align the generated size internally for this latent format. Exact mode only accepts already valid sizes. See Resolution controls below.

Metadata describes the planned clip. If downstream nodes change frame count, resolution or FPS, that metadata must be updated. This node does not generate speech, force TTS duration, mix audio, or perform lip sync.

## Install

Extract the ZIP so that `ComfyUI/custom_nodes/VideoControl/__init__.py` exists, then restart ComfyUI. Search for **ComfyUI-Video-Control** under **ComfyUI / Video / Control**.

Install from [the repository](https://github.com/AmanDolorain/ComfyUI-Video-Control) using your Manager's Git URL installation option, if available, or run this from `ComfyUI/custom_nodes`:

```bash
git clone https://github.com/AmanDolorain/ComfyUI-Video-Control.git
```

Do not install a second copy alongside the extracted version.

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

## Resolution controls

Choose `resolution_preset = Custom` to use the width and height fields. They accept whole pixels with a step of 1; you do not need to calculate multiples yourself. Selecting any other preset overrides both fields with the preset's requested dimensions. Preset names describe the **requested** size, before rounding.

| size_rounding | Behavior |
| --- | --- |
| `nearest` (default) | Closest internally valid size; ties round upward |
| `down` | Round each dimension downward; use this to avoid increasing normal requested dimensions |
| `up` | Round each dimension upward |
| `exact` | Keep the exact dimensions if supported; otherwise show an error instead of silently changing them |

The latent format still requires internally aligned dimensions. Automatic modes handle alignment to 16 pixels for you. `exact` therefore accepts multiples of 16; unsupported exact sizes require a separate resize after decoding if you need an exact delivery resolution. The smallest internally representable size here is 16 x 16. Inputs below 16 round to 16 even in `down` mode.

| Request | Mode | Actual generated size |
| --- | --- | --- |
| 854 x 479 | nearest | 848 x 480 |
| 854 x 479 | down | 848 x 464 |
| 854 x 479 | up | 864 x 480 |
| 1920 x 1080 | nearest | 1920 x 1088 |
| 1920 x 1080 | down | 1920 x 1072 |
| 3840 x 2160 (UHD 4K) | nearest or exact | 3840 x 2160 |
| 4096 x 2160 (DCI 4K) | nearest or exact | 4096 x 2160 |
| 1 x 1 | nearest, down or up | 16 x 16 |

Each dimension rounds independently, so the aspect ratio can change slightly. The node does not resize or crop input images. Connect its **width and height outputs**, rather than unrounded input values, to other resolution controls. Both metadata and latent allocation use the actual dimensions. The summary reports requested and actual size.

Presets include 64, 128 and 256 pixel squares, 360p, 480p, 512 square, 720p, 1080p, 1440p, UHD 4K, DCI 4K and portrait options. Small sizes are useful for trying the workflow, but the model may impose a larger minimum or have poor results at those sizes. 4K sizing support is not a guarantee that direct 4K generation fits your GPU. Memory also depends on model, duration, precision and other nodes. This node does not select a resolution from your VRAM or change the model's latent format.

## Updating from 1.0.7

The node ID and all eight output sockets are unchanged. New resolution controls are optional and default to Custom / nearest, so existing valid resolutions keep their size. If the controls do not appear after updating, restart ComfyUI, refresh the browser and add a fresh Video Control node, then reconnect the existing wires. Width and height outputs always mean the actual generated dimensions.

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

## Author credit display

The frontend extension in `web/author.js` draws a small, muted author credit at the actual bottom-right boundary of the canvas node, on the footer line beside the lower-left package badge. It follows the node boundary after resizing. The credit is no longer a DOM widget below the controls and has no clickable overlay. The renderer reserves 24 pixels of footer space to keep controls clear.

This implementation uses the classic LiteGraph canvas rendering hook. Alternate renderers such as Nodes 2.0 may not draw that hook; author attribution remains in the node description. Actual placement must be checked in your installed frontend. After updating, restart ComfyUI, hard-refresh the browser (Ctrl+F5) and add a fresh node if necessary.

## Names and discovery

Search for **ComfyUI-Video-Control**. The Registry/Manager display name and the default canvas title both use that spelling, with hyphens. The category remains `ComfyUI/Video/Control`. The immutable package ID remains `comfyui-video-control`, and the registered node ID remains `VideoControl`, preserving workflow links. Existing saved workflows may retain their old node titles until a fresh node is added.

The description includes duration, FPS, resolution presets, automatic rounding, empty latent and VHS metadata. Listing cache refresh and registry metadata processing can delay a title change. Search placement, ratings and ranking are controlled by the listing service; no top-position guarantee is made.
