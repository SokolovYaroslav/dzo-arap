import argparse
import datetime
import json
import os
import cv2

from tqdm import tqdm
from classes.CWrapper import CWrapper
from classes.Grid import Grid
from classes.ImageHelper import ImageHelper
from math_utils import smooth_poses


def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")



class NoGuiRunner:
    def __init__(self, args):
        self._cw = CWrapper()
        self._args = args
        path = args.path

        self._grid = None
        self._image = None
        self._handles = None
        self.load_image(path)




    def run(self):
        self._grid = Grid(self._cw, self._image, self._args, gui=False)

        kpt_files = os.listdir(self._args.keypoints_dir)
        kpt_files.sort(key=lambda e: int(e.split('_')[0]))
        self._handles = self.add_bunch(os.path.join(self._args.keypoints_dir, kpt_files[0]))

        #smooth_poses(self._args.keypoints_dir, kpt_files[1:], 5)

        if not os.path.exists(self._args.output_dir):
            os.mkdir(self._args.output_dir)

        pose_num = 0
        cv2.imwrite(os.path.join(self._args.output_dir, '{}.png'.format(pose_num)),
                    self._image._data[:, :, ::-1])

        for pose in tqdm(kpt_files[1:]):
            self.move_bunch(pose)
            pose_num += 1
            for _ in range(self._args.num_iterations):
                self.run_once()
            cv2.imwrite(os.path.join(self._args.output_dir, '{}.png'.format(pose_num)),
                        self._image._data[:, :, ::-1])

    def run_once(self):
        # no time delay left
        self._grid.regularize()
        self._grid.project()



    def load_image(self, path):
            self._image = ImageHelper(self._cw, self._args, gui=False)

    def add_bunch(self, posepath):
        with open(posepath, 'r') as f:
            poss = json.load(f)
        kpts = poss['people'][0]['pose_keypoints_2d']
        xs = kpts[::3]
        ys = kpts[1::3]
        new_handles = {}
        i = 0
        for ptx, pty in zip(xs, ys):
            new_handles[i] = (ptx, pty)
            i += 1
        self._grid.create_bunch_cp(new_handles=new_handles)
        return new_handles

    def move_bunch(self, filename):
        with open(os.path.join(self._args.keypoints_dir, filename)) as f:
            poss = json.load(f)
        newpos = poss['people'][0]['pose_keypoints_2d']
        xs = newpos[::3]
        ys = newpos[1::3]
        for i, h_obj in self._handles.items():
            self._grid.set_control_target(i, xs[i], ys[i])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask", default=None, help="custom mask path")
    parser.add_argument("--box_size", default=10, type=int, help="box size for grid")
    parser.add_argument("--keypoints_dir", help="path to keypoints directory")
    parser.add_argument("--path", default="assets/sokolov_228.jpg", help="path to image")
    parser.add_argument("--save_mask", default=str2bool, help="to save computed mask into masks/")
    parser.add_argument("--output_dir", help="directory to write the result")
    parser.add_argument("--num_iterations", default=50, help="number of iterations to fit each pose")
    parser.add_argument(
        "--control_weight", default=100000, type=int, help="control weight for grid"
    )

    runner = NoGuiRunner(parser.parse_args())
    runner.run()
