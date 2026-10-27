import importlib.util
import pathlib
import sys
import types
import unittest
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('video_control',root/'__init__.py',submodule_search_locations=[str(root)])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
from video_control.calculations import make_plan, RESOLUTION_PRESETS, resolve_resolution

class Tests(unittest.TestCase):
    def test_current_workflow(self):
        p=make_plan(5,25,848,480)
        self.assertEqual(p.frame_count,125);self.assertEqual(p.actual_seconds,5)
        self.assertEqual(p.latent_shape,(1,16,32,60,106))
        self.assertEqual(p.video_info()['loaded_frame_count'],125)
        self.assertEqual(len(p.video_info()),10)
    def test_rounding_and_audio_duration(self):
        for mode, expected in [('nearest',121),('at_least',121),('at_most',117)]:
            p=make_plan(5,24,848,480,mode)
            self.assertEqual(p.frame_count,expected)
            self.assertEqual(p.actual_seconds,expected/24)
            self.assertEqual(p.video_info()['loaded_duration'],p.actual_seconds)
    def test_many_durations(self):
        for fps in [1,12,24,25,30,60]:
            for seconds in [.1,1,5,6,7,8,10,30]:
                p=make_plan(seconds,fps,512,512)
                self.assertEqual((p.frame_count-1)%4,0)
                self.assertEqual(4*(p.latent_shape[2]-1)+1,p.frame_count)
                self.assertLessEqual(abs(p.frame_count-seconds*fps),2)
    def test_validation(self):
        for kw in [dict(fps=0),dict(fps=29.97),dict(duration_seconds=float('nan')),
                   dict(width=0),dict(batch_size=2),dict(duration_seconds=600,fps=120),
                   dict(width=16385),dict(height=True),dict(width=5.5)]:
            args=dict(duration_seconds=5,fps=25,width=848,height=480);args.update(kw)
            with self.assertRaises(ValueError):make_plan(**args)
    def test_custom_size_rounding(self):
        expected = {'nearest': (848, 480), 'down': (848, 464), 'up': (864, 480)}
        for mode, size in expected.items():
            p=make_plan(5,25,854,479,size_rounding=mode)
            self.assertEqual((p.width,p.height),size)
            self.assertEqual((p.requested_width,p.requested_height),(854,479))
            self.assertEqual(p.latent_shape[-2:],(size[1]//8,size[0]//8))
            self.assertEqual(p.video_info()['loaded_width'],size[0])
            self.assertEqual(p.video_info()['source_height'],size[1])
            self.assertIn(f'Actual size: {size[0]}x{size[1]}',p.summary())
    def test_exact_size_is_not_silently_changed(self):
        p=make_plan(5,25,3840,2160,size_rounding='exact')
        self.assertEqual((p.width,p.height),(3840,2160))
        with self.assertRaisesRegex(ValueError,'Exact size'):
            make_plan(5,25,854,480,size_rounding='exact')
    def test_all_presets_and_smallest_size(self):
        for preset, requested in RESOLUTION_PRESETS.items():
            if requested is None: continue
            p=make_plan(5,25,13,17,resolution_preset=preset)
            self.assertEqual((p.requested_width,p.requested_height),requested)
            self.assertEqual(p.width%16,0);self.assertEqual(p.height%16,0)
        for mode in ('nearest','down','up'):
            self.assertEqual(resolve_resolution(1,1,size_rounding=mode),(1,1,16,16))
        p=make_plan(5,25,3840,2160)
        self.assertEqual(p.latent_shape[-2:],(270,480))
    def test_rounding_boundaries_and_unknown_modes(self):
        for n in range(1,16385):
            for mode in ('nearest','down','up'):
                _,_,w,h=resolve_resolution(n,n,size_rounding=mode)
                self.assertTrue(16<=w<=16384);self.assertEqual(w%16,0)
                self.assertEqual(w,h)
                if mode=='nearest':self.assertLessEqual(abs(w-n),max(8,16-n))
                if mode=='down' and n>=16:self.assertLessEqual(w,n)
                if mode=='up':self.assertGreaterEqual(w,n)
        for kwargs in (dict(size_rounding='typo'),dict(resolution_preset='typo')):
            with self.assertRaises(ValueError):resolve_resolution(512,512,**kwargs)
    def test_widget_contract_and_legacy_defaults(self):
        fields=module.VideoControl.INPUT_TYPES()
        self.assertEqual(fields['required']['width'][1]['step'],1)
        self.assertEqual(fields['required']['height'][1]['min'],1)
        p=make_plan(5,25,848,480)
        self.assertEqual((p.width,p.height),(848,480))
    def test_node_contract_with_mock_tensor_backend(self):
        # This verifies the tensor request and returned sockets, not PyTorch inference.
        torch=types.ModuleType('torch');torch.zeros=lambda shape,device:dict(shape=shape,device=device)
        comfy=types.ModuleType('comfy');mm=types.ModuleType('comfy.model_management')
        mm.intermediate_device=lambda:'cpu';comfy.model_management=mm
        old={k:sys.modules.get(k) for k in ('torch','comfy','comfy.model_management')}
        sys.modules.update({'torch':torch,'comfy':comfy,'comfy.model_management':mm})
        try:
            out=module.VideoControl().build(5,25,848,480)['result']
            self.assertEqual(len(out),len(module.VideoControl.RETURN_TYPES))
            self.assertEqual(out[0]['samples']['shape'],(1,16,32,60,106))
            self.assertEqual(out[0]['downscale_ratio_spacial'],8)
            self.assertEqual(out[1]['loaded_fps'],out[3]);self.assertEqual(out[2],125)
            self.assertEqual(out[4],5)
            for kwargs, size in [
                (dict(width=854,height=479),(848,480)),
                (dict(width=1920,height=1080,size_rounding='up'),(1920,1088)),
                (dict(width=1,height=1),(16,16)),
                (dict(width=848,height=480,resolution_preset='4K UHD 3840 x 2160'),(3840,2160)),
            ]:
                args=dict(duration_seconds=5,fps=25,width=848,height=480);args.update(kwargs)
                result=module.VideoControl().build(**args)['result']
                self.assertEqual(result[5:7],size)
                self.assertEqual(result[0]['samples']['shape'][-2:],(size[1]//8,size[0]//8))
                self.assertEqual((result[1]['loaded_width'],result[1]['loaded_height']),size)
        finally:
            for k,v in old.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v
if __name__=='__main__':unittest.main()
