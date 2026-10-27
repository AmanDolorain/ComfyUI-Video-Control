# ComfyUI-Video-Control

Author: **Aman Dolorain** · Version **1.2.0**

Shared video timing, resolution, image-to-video preparation and planned VHS metadata in one node.

## What changed

Connect `positive`, `vae` and `start_image` directly to this controller. It now delegates reference-image resizing, VAE encoding, masks and conditioning to ComfyUI's native image-to-video implementation. A separate image-to-video preparation node is unnecessary for this supported path.

The original eight output sockets keep their positions. The new `positive` output is appended as output 9. Existing empty-latent workflows continue to work with all three new inputs disconnected. Connecting only some of them raises a clear error.

## Image-to-video wiring

| Source | Destination |
| --- | --- |
| CLIP Text Encode: CONDITIONING | Controller: positive input |
| Matching Load VAE: VAE | Controller: vae input |
| Load Image: IMAGE | Controller: start_image input |
| Controller: positive output | BasicGuider: conditioning |
| Controller: latent | SamplerCustomAdvanced: latent_image |
| Controller: fps | Create Video: fps |
| Controller: actual_duration_seconds | MMAudio Sampler: duration |
| SamplerCustomAdvanced: output | VAE Decode: samples |
| Matching Load VAE: VAE | VAE Decode: vae |
| VAE Decode: IMAGE | Create Video: images and MMAudio Sampler: images |
| MMAudio Sampler: audio | Create Video: audio |
| Create Video: VIDEO | Save Video: video |

Keep RandomNoise, KSamplerSelect, BasicScheduler and BasicGuider connected to SamplerCustomAdvanced as usual. Send the same patched MODEL to BasicGuider and BasicScheduler. The controller does not load models or replace a sampler.

Remove the separate image-to-video preparation node after reconnecting its conditioning and latent paths. Width, height and length are passed internally; do not keep that duplicate preparation branch. FPS remains a playback/timing setting, not an image-conditioning input.

## Inputs and modes

`duration_seconds`, `fps`, `width`, `height`, `frame_rounding`, `batch_size`, `resolution_preset` and `size_rounding` retain their previous meanings. All three optional sockets connected select image-to-video mode; none connected selects empty-latent mode.

`guidance_type` must match the checkpoint: `v1 (concat)` is the default and matches the previously wired workflow; `v2 (replace)` and `custom` are passed unchanged to the native backend. Do not select one merely to improve quality.

## Compatibility and resolution

This is **not a universal latent generator**. Image-to-video uses the native `HunyuanImageToVideo` implementation in `comfy_extras.nodes_hunyuan`. It requires a matching video checkpoint, conditioning and video VAE. It does not support H3, Wan or arbitrary image checkpoints merely because their sockets connect. Empty mode creates `[1, 16, (frames-1)/4+1, height/8, width/8]`.

Custom sizes, including 512 x 512, and presets through 4K are available. Automatic nearest/down/up rounding aligns actual dimensions to 16 pixels; exact mode rejects unaligned sizes. Dimensions as small as 16 x 16 can be represented, but this is not a model-quality guarantee. Large resolutions require suitable hardware. Frame counts align to 4n+1 and actual duration is frame_count / FPS. One video per run; whole-number FPS only.

The native backend center-crops/resizes the reference image. A square source can therefore lose edges when the requested aspect ratio differs. The controller preserves native conditioning and masks, including the noise mask used by replace guidance.

## Outputs

`latent`, `video_info`, `frame_count`, `fps`, `actual_duration_seconds`, `width`, `height`, `summary`, `positive`.

`positive` is modified image conditioning in image-to-video mode and is `None` in empty mode. Do not connect this output to a guider in empty mode; use your original text conditioning there.

`video_info` is a VHS_VIDEOINFO dictionary of planned settings, not a video file and not a measurement of generated frames. `summary` connects to Preview as Text. Neither is empty simply because no downstream consumer is attached. If later processing changes timing or dimensions, update that metadata accordingly.

## Install and update

Install from `https://github.com/AmanDolorain/ComfyUI-Video-Control` using ComfyUI Manager or clone into `ComfyUI/custom_nodes`. Restart ComfyUI and refresh the browser. No extra pip requirements or model downloads are introduced. Image-to-video mode needs ComfyUI with the native backend installed. The extension imports that backend only when execution needs it.

After upgrading, save a workflow backup and add a fresh controller if the existing instance has not refreshed its sockets. Existing output indices and numeric widget order are preserved. Reconnect the three inputs and the new positive output explicitly. Keep the existing product, publisher and author names.

## Verification

Run `python -m unittest discover -s tests -v`. Tests cover planning, previous output positions, legacy empty mode, partial-input errors, native API forwarding, V3/tuple return handling, and preservation of native conditioning/masks. These are isolated tests with a mocked tensor/backend; they do not establish actual generation quality. A real ComfyUI model run is still required. See VERIFICATION.md.

The controller does not generate speech, force TTS duration, mix audio or perform lip sync.
