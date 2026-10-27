import sys
import types
import unittest
from unittest.mock import patch
from test_node import module

class ImageVideoTests(unittest.TestCase):
    def test_existing_output_positions_are_unchanged(self):
        self.assertEqual(module.VideoControl.RETURN_NAMES[:8],
                         ('latent','video_info','frame_count','fps','actual_duration_seconds','width','height','summary'))
        self.assertEqual(module.VideoControl.RETURN_TYPES[-1], 'CONDITIONING')

    def test_partial_connections_fail_before_allocating(self):
        for inputs in ({'positive':[]}, {'vae':object()}, {'start_image':object()},
                       {'positive':[], 'vae':object()}, {'vae':object(),'start_image':object()}):
            with self.subTest(inputs=inputs), self.assertRaisesRegex(ValueError,'all three'):
                module.VideoControl().build(5,25,512,512,**inputs)

    def test_native_conditioning_and_latent_preserved(self):
        for method in ('execute','encode'):
            for v3 in (True, False):
                captured={}
                conditioning=object()
                latent={'samples':object(),'noise_mask':object()}
                def run(**kwargs):
                    captured.update(kwargs)
                    values=(conditioning,latent)
                    return types.SimpleNamespace(result=values) if v3 else values
                native=types.ModuleType('comfy_extras.nodes_hunyuan')
                native.HunyuanImageToVideo=type('Native',(),{method:staticmethod(run)})
                image=object(); vae=object(); positive=[]
                with patch.dict(sys.modules, {'comfy_extras.nodes_hunyuan':native}):
                    result=module.VideoControl().build(5,25,854,479,positive=positive,
                        vae=vae,start_image=image,guidance_type='v2 (replace)')['result']
                self.assertIs(result[0],latent);self.assertIs(result[8],conditioning)
                self.assertEqual(captured,dict(positive=positive,vae=vae,start_image=image,
                    width=848,height=480,length=125,batch_size=1,guidance_type='v2 (replace)'))
                self.assertEqual(result[1]['loaded_frame_count'],125)
                self.assertEqual(result[4],5)
                self.assertIn('Image-to-video',result[7])

    def test_backend_missing_and_bad_result(self):
        native=types.ModuleType('comfy_extras.nodes_hunyuan')
        with patch.dict(sys.modules, {'comfy_extras.nodes_hunyuan':native}):
            with self.assertRaisesRegex(RuntimeError,'Update ComfyUI'):
                module.VideoControl().build(5,25,512,512,positive=[],vae=object(),start_image=object())
        native.HunyuanImageToVideo=type('Native',(),{'execute':staticmethod(lambda **kw: ([],{}))})
        with patch.dict(sys.modules, {'comfy_extras.nodes_hunyuan':native}):
            with self.assertRaisesRegex(RuntimeError,'samples latent'):
                module.VideoControl().build(5,25,512,512,positive=[],vae=object(),start_image=object())

    def test_invalid_guidance(self):
        with self.assertRaisesRegex(ValueError,'guidance_type'):
            module.VideoControl().build(5,25,512,512,guidance_type='wrong')
