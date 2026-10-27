"""Video Control: settings + 16-channel video format empty latent + VHS video metadata.
No external downloads, model loading, disk encoding, or network calls.
"""
__author__ = "Aman"
__version__ = "1.1.1"
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
            'resolution_preset': (list(RESOLUTION_PRESETS), {'default':'Custom',
                'tooltip':'Custom uses width/height. Other presets override both values.'}),
            'size_rounding': (['nearest','down','up','exact'], {'default':'nearest',
                'tooltip':'Auto-align size for the latent format. Exact preserves valid sizes or reports an error. '
                          'Actual dimensions are shown in summary and width/height outputs.'}),
        }}

    # 2. Every output's position must match the position in the returned tuple.
    RETURN_TYPES = ('LATENT','VHS_VIDEOINFO','INT','FLOAT','FLOAT','INT','INT','STRING')
    RETURN_NAMES = ('latent','video_info','frame_count','fps','actual_duration_seconds','width','height','summary')
    FUNCTION = 'build'
    CATEGORY = 'Video/Control'
    DESCRIPTION = 'Author: Aman. Shared video settings and a 16-channel video empty latent. Not other latent formats.'

    # 3. ComfyUI runs this method only when this node's outputs are needed.
    def build(self, duration_seconds, fps, width, height, frame_rounding='nearest', batch_size=1,
              resolution_preset='Custom', size_rounding='nearest'):
        plan = make_plan(duration_seconds, fps, width, height, frame_rounding, batch_size,
                         resolution_preset, size_rounding)
        # Use ComfyUI's existing torch/device setup. No separate pip installation.
        import torch
        import comfy.model_management
        samples = torch.zeros(plan.latent_shape,
                              device=comfy.model_management.intermediate_device())
        # Exact 16-channel video format layout: [batch, 16 channels, temporal, height/8, width/8].
        latent = {'samples':samples, 'downscale_ratio_spacial':8}
        summary = plan.summary()
        print('[Video Control] ' + summary.replace('\n',' | '))
        result = (latent, plan.video_info(), plan.frame_count, plan.fps,
                  plan.actual_seconds, plan.width, plan.height, summary)
        return {'ui': {'text':[summary]}, 'result':result}

# 4. Registration lets ComfyUI discover the node and its searchable display name.
NODE_CLASS_MAPPINGS = {'VideoControl':VideoControl}
NODE_DISPLAY_NAME_MAPPINGS = {'VideoControl':'Video Control'}
