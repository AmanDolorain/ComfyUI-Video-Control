"""Video Control: settings + 16-channel video format empty latent + VHS video metadata.
No external downloads, model loading, disk encoding, or network calls.
"""
__author__ = "Aman Dolorain"
__version__ = "1.2.0"
WEB_DIRECTORY = "./web"

from .calculations import make_plan, RESOLUTION_PRESETS

class VideoControl:
    # 1. INPUT_TYPES defines the controls visible on the node.
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'duration_seconds': ('FLOAT', {'default':5.0, 'min':0.01, 'max':600.0, 'step':0.1}),
            'fps': ('FLOAT', {'default':25.0, 'min':1.0, 'max':120.0, 'step':1.0,
                             'tooltip':'Whole-number FPS for your current LatentSync wrapper.'}),
            'width': ('INT', {'default':848, 'min':1, 'max':16384, 'step':1,
                              'tooltip':'Requested width. Used when resolution_preset is Custom.'}),
            'height': ('INT', {'default':480, 'min':1, 'max':16384, 'step':1,
                               'tooltip':'Requested height. Used when resolution_preset is Custom.'}),
            'frame_rounding': (['nearest','at_least','at_most'], {'default':'nearest'}),
            'batch_size': ('INT', {'default':1, 'min':1, 'max':1,
                                 'tooltip':'One video per run; multi-video metadata is not supported.'}),
        }, 'optional': {
            'positive': ('CONDITIONING',),
            'vae': ('VAE',),
            'start_image': ('IMAGE',),
            'resolution_preset': (list(RESOLUTION_PRESETS), {'default':'Custom',
                'tooltip':'Custom uses width/height. Other presets override both values.'}),
            'size_rounding': (['nearest','down','up','exact'], {'default':'nearest',
                'tooltip':'Auto-align size for the latent format. Exact preserves valid sizes or reports an error. '
                          'Actual dimensions are shown in summary and width/height outputs.'}),
            'guidance_type': (['v1 (concat)', 'v2 (replace)', 'custom'], {'default':'v1 (concat)',
                'tooltip':'Must match the video checkpoint. v1 (concat) matches the existing workflow.'}),
        }}

    # 2. Every output's position must match the position in the returned tuple.
    RETURN_TYPES = ('LATENT','VHS_VIDEOINFO','INT','FLOAT','FLOAT','INT','INT','STRING','CONDITIONING')
    RETURN_NAMES = ('latent','video_info','frame_count','fps','actual_duration_seconds','width','height','summary','positive')
    FUNCTION = 'build'
    CATEGORY = 'ComfyUI/Video/Control'
    DESCRIPTION = 'Author: Aman Dolorain. Shared timing, resolution and metadata with optional native image-to-video preparation. Requires a matching 16-channel video model and VAE.'

    # 3. ComfyUI runs this method only when this node's outputs are needed.
    def build(self, duration_seconds, fps, width, height, frame_rounding='nearest', batch_size=1,
              resolution_preset='Custom', size_rounding='nearest', positive=None, vae=None,
              start_image=None, guidance_type='v1 (concat)'):
        plan = make_plan(duration_seconds, fps, width, height, frame_rounding, batch_size,
                         resolution_preset, size_rounding)
        if guidance_type not in ('v1 (concat)', 'v2 (replace)', 'custom'):
            raise ValueError('Unknown guidance_type.')
        provided = (positive is not None, vae is not None, start_image is not None)
        if any(provided) and not all(provided):
            raise ValueError('Image-to-video requires all three inputs: positive, vae and start_image. '
                             'Disconnect all three for the legacy empty-latent mode.')
        if all(provided):
            # Delegate image resizing, encoding, masks and conditioning to ComfyUI.
            # Do not recreate these model-specific operations in this extension.
            from .i2v import prepare_image_video
            positive, latent = prepare_image_video(
                positive, vae, start_image, plan.width, plan.height,
                plan.frame_count, batch_size, guidance_type)
            mode = 'Image-to-video | ' + guidance_type
        else:
            import torch
            import comfy.model_management
            samples = torch.zeros(plan.latent_shape,
                                  device=comfy.model_management.intermediate_device())
            latent = {'samples': samples, 'downscale_ratio_spacial': 8}
            mode = 'Empty latent (no reference image)'
        summary = mode + '\n' + plan.summary()
        print('[Video Control] ' + summary.replace('\n',' | '))
        result = (latent, plan.video_info(), plan.frame_count, plan.fps,
                  plan.actual_seconds, plan.width, plan.height, summary, positive)
        return {'ui': {'text':[summary]}, 'result':result}

# 4. Registration lets ComfyUI discover the node and its searchable display name.
NODE_CLASS_MAPPINGS = {'VideoControl':VideoControl}
NODE_DISPLAY_NAME_MAPPINGS = {'VideoControl':'ComfyUI-Video-Control'}
