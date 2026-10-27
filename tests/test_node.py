import importlib.util
import pathlib
import sys
import types
import unittest
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('video_control',root/'__init__.py',submodule_search_locations=[str(root)])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
from video_control.calculations import make_plan

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
                   dict(width=850),dict(batch_size=2),dict(duration_seconds=600,fps=120)]:
            args=dict(duration_seconds=5,fps=25,width=848,height=480);args.update(kw)
            with self.assertRaises(ValueError):make_plan(**args)
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
        finally:
            for k,v in old.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v
if __name__=='__main__':unittest.main()
