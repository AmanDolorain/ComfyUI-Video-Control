# Verification — 1.2.0

15 isolated unit tests pass. No real ComfyUI inference or GPU generation was run in the build environment.

The adapter was checked against the upstream `comfy_extras/nodes_hunyuan.py` source fetched on 2026-10-27. Native execute accepts positive, vae, width, height, length, batch_size, guidance_type and start_image and returns conditioning plus latent. Current NodeOutput.result and legacy tuple returns are supported. The old encode method alias is also supported.

Tests verify input completeness, forwarded actual rounded dimensions and frame count, output indices, metadata, and preservation of returned conditioning and noise masks. These are mocked integration contracts, not a substitute for inference.

## On-machine acceptance test

1. Save a backup of the workflow. Update/restart ComfyUI and refresh the browser.
2. Add a fresh controller. Confirm three image-to-video inputs and the final positive output.
3. Use matching video models/VAE. Connect all three inputs, positive output to BasicGuider and latent to sampler.
4. For 5 seconds, 25 FPS, 848 x 480, confirm 125 frames and a 5-second planned summary.
5. With a fixed seed and identical inputs/settings, compare the controller branch to a separate native image-to-video node branch. Use one branch at a time; both call the same native preparation API.
6. Check 512 x 512, rounded custom size, and legacy empty mode. Do not attempt a 4K test unless hardware permits it.
7. Confirm actual decoded frame count and saved FPS; planned metadata alone is not a measurement.
8. Confirm Author: Aman Dolorain remains in the footer. web/author.js is unchanged from 1.1.6.
