# Changelog

## 1.1.5

- Use ComfyUI-Video-Control as the Registry/Manager display name and canvas node title.
- Expand the description with accurate feature search terms.
- Replace the author widget row with credit anchored to the bottom-right canvas footer.
- Keep the package ID, node ID, controls and outputs unchanged.


## 1.1.4

- Set Registry/Manager display name to ComfyUI / Video / Control.
- Set canvas search category to ComfyUI/Video/Control.
- Preserve the Video Control node title, package ID, registered node ID and output sockets.


## 1.1.3

- Move author credit to the right side of a compact footer row.
- Use smaller, muted text and reduce footer height from 24 to 18 pixels.
- Keep all backend controls, output sockets and calculations unchanged.


## 1.1.2

- Configure Comfy Registry publisher amandolorain.
- Add a GitHub Actions publishing workflow, gated by the Python tests.
- Document publishing secrets, releases and verification.


## 1.1.1

- Show a read-only Author: Aman label inside Video Control.
- Add author attribution to the node description.
- Keep node name, ID, inputs and outputs unchanged.

## 1.1.0

- Accept custom dimensions in one-pixel increments.
- Add automatic nearest/down/up rounding and an exact-size validation mode.
- Add small-resolution, landscape, portrait and UHD/DCI 4K presets.
- Report requested and actual dimensions in the summary.
- Keep latent allocation, dimension outputs and planned video metadata consistent.
- Preserve the existing node ID and output order; new controls have backward-compatible defaults.
- Document internal alignment, aspect-ratio changes, GPU limits and exact-output limitations.

## 1.0.7

- Use the neutral Video Control product name, with Aman as author.
