"""Adapter to ComfyUI's native image-to-video implementation; no model downloads."""
import importlib


def prepare_image_video(positive, vae, start_image, width, height, length,
                        batch_size, guidance_type):
    try:
        module = importlib.import_module('comfy_extras.nodes_hunyuan')
        implementation = module.HunyuanImageToVideo
    except (ImportError, AttributeError) as error:
        raise RuntimeError('Native image-to-video support is unavailable. Update ComfyUI '
                           'and restart it; the controller does not install a replacement backend.') from error
    execute = getattr(implementation, 'execute', None)
    if execute is None:
        execute = getattr(implementation, 'encode', None)
    if not callable(execute):
        raise RuntimeError('Unsupported native image-to-video API. Update ComfyUI.')
    result = execute(positive=positive, vae=vae, start_image=start_image,
                     width=width, height=height, length=length,
                     batch_size=batch_size, guidance_type=guidance_type)
    # Current V3 NodeOutput and older tuple API.
    values = result.result if hasattr(result, 'result') else result
    if not isinstance(values, (tuple, list)) or len(values) != 2:
        raise RuntimeError('Unexpected native image-to-video return contract.')
    conditioning, latent = values
    if not isinstance(latent, dict) or 'samples' not in latent:
        raise RuntimeError('Native image-to-video did not return a samples latent.')
    return conditioning, latent
