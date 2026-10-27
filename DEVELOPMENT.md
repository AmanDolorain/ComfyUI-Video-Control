# How this custom node works

Author: Aman

## Project structure

- `__init__.py` defines the node controls, outputs, execution method and registration.
- `calculations.py` contains timing validation, frame rounding and metadata generation.
- `tests/test_node.py` tests calculations and the runtime interface with mocked dependencies.
- `pyproject.toml` records package metadata, including the author and version.

## Build a custom node step by step

1. Create a directory inside `ComfyUI/custom_nodes` and add `__init__.py`.
2. Define a Python class. Its `INPUT_TYPES` method describes each control and socket type.
3. Set `RETURN_TYPES` and `RETURN_NAMES` in the same order as the returned values.
4. Set `FUNCTION` to the name of the execution method, here `build`.
5. Implement the method to read inputs and return results. Keep independent calculations in a separate module when useful.
6. Register the class in `NODE_CLASS_MAPPINGS`. Set its searchable name in `NODE_DISPLAY_NAME_MAPPINGS`.
7. Restart ComfyUI. If importing fails, inspect the startup console for the full Python error.

## Resolution handling

`resolution_preset` and `size_rounding` are optional inputs appended after the existing controls. Existing output positions and the node registration ID remain unchanged. `resolve_resolution` validates custom input or selects a preset, then aligns the output dimensions. It returns requested width, requested height, actual width and actual height. All tensor allocation, dimension outputs and VHS metadata use actual dimensions.

The width and height widgets now use a minimum of 1 and a step of 1. Internal alignment remains 16 for the supported latent format; changing the input controls does not change the model architecture. Exact mode rejects unsupported sizes. Automatic modes clamp dimensions smaller than 16 to 16. A preset overrides both custom input dimensions. Rounding is independent per dimension and can change aspect ratio slightly.

## Timing and tensor allocation

The calculation module converts seconds and FPS into a frame count satisfying `4n + 1`. The selected rounding mode determines whether to choose the nearest, higher or lower valid count. Actual duration is frame count divided by FPS.

The execution method allocates a zero tensor through ComfyUI's existing PyTorch and device configuration. Its shape is `[1, 16, (frames-1)/4+1, height/8, width/8]`. It does not load model weights or generate video itself. Only models accepting this specific latent format are compatible.

The node also returns a planned `VHS_VIDEOINFO` dictionary. It is not a measurement of the final video. Any downstream changes to FPS, dimensions or frame count require updated metadata.

## Workflow migration

Save a copy of your workflow before replacing nodes. Connect the control node's outputs to all consumers before removing old duration, FPS, calculation and empty latent nodes. An intermediate video save/select/reload chain can be removed when it exists solely to obtain planned metadata. Keep the final video creator, model, sampler, VAE, audio generator, mixer and lip-sync nodes.

Speech duration is not automatically controlled by this node. Dialogue may need trimming, padding or regeneration to match the planned clip. A mixer must mix tracks simultaneously rather than concatenate them if dialogue and background sound should overlap.

## Tests

From the project directory, run:

```bash
python -m unittest discover -s tests -v
```

These tests cover calculations and a mocked runtime contract. They do not test actual PyTorch allocation, full ComfyUI execution, model compatibility, generation quality or lip-sync accuracy. Validate those in a real workflow.
