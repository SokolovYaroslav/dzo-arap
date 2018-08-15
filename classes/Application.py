import tkinter as tk
from datetime import datetime

from classes.ImageHelper import ImageHelper
from classes.Grid import Grid
from classes.CWrapper import CWrapper
from classes.utils import *
from classes.utils import smooth_poses, get_poses
import cv2
import os
import numpy as np
from collections import OrderedDict
from PIL import Image

def save_image(path, img):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.mkdir(dir)
        print("Created directory", dir)
    res = cv2.imwrite(path, img[:, :, ::-1])
    if res:
        print("Successfully saved image into", path)
    else:
        print("Couldn't save image into", path)

def get_path(path_var, orig_path, index):
    if orig_path is not None and orig_path is not False:
       name = orig_path.split('/')[-1].split('.')[-2]
       if index[0] == 0:
           path_var.set(path_var.get().replace(name, name + str(index[0])))
       else:
           path_var.set(path_var.get().replace(name + str(index[0] - 1), name + str(index[0])))
       index[0] += 1
    return path_var.get()

class Application:

    def __init__(self, args):
        self._cw = CWrapper()
        self._args = args
        path = args.path

        self._window = tk.Tk()

        self._grid = None
        self._image = None
        self.load_image(path)

        self._canvas = tk.Canvas(self._window, width=self._image.width, height=self._image.height)
        self._canvas.pack()

        frame_index = [0]
        self._img_path = tk.StringVar()
        self._img_path.set('out/' + path.split('/')[-1])
        self._entry = tk.Entry(self._window, textvariable=self._img_path)
        def save(*a):
            save_image(get_path(self._img_path, orig_path=(args.enumerate and args.path), index=frame_index),
                       self._image._data.copy()
            )
        self._button = tk.Button(self._window, text="Save", command=save)
        self._entry.pack(side=tk.LEFT, padx=(30,20), expand=True, fill=tk.BOTH)
        self._button.pack(side=tk.RIGHT, padx=(10, 30))
        self._window.bind("<space>", save)

        self._image.canvas = self._canvas

        self._active_handle = -1
        self._loop = None
        self._t_last = 0

    def load_image(self, path):
        self._image = ImageHelper(self._cw, self._args)

    def bind(self, event, fn):
        self._canvas.bind(event, fn)

    def custom_save(self, epoch):
        path = 'out/'+str(epoch)+'.png'
        save_image(path, self._image._data)

    def run(self):
        self._grid = Grid(self._cw, self._image, self._args)


        poses = get_poses(self._args.keypoints_dir, with_hands=True, interpolate_hands=True)
        self._handles, self._foundmask = self.add_bunch(poses[0])
        self._smoothed = smooth_poses(poses[1:], win_length=5)


        self._add_border_points(self._args.num_bodypart_points, self._args.visible_bodypart_points)

        self._image.draw()
        self._grid.draw()

        global epoch, it
        it = epoch = 1
        self.custom_save(epoch)
        self.move_bunch(1)
        print('Epoch {0} started'.format(1))

        self._run_once()

        self._window.mainloop()


    def _run_once(self):

        self._grid.regularize()
        global it, epoch
        dt = datetime.now()
        delta = dt.timestamp()-self._t_last
        if 0 < delta > 0.03:  # 0.03 - 30 FPS

            # dt = datetime.now()
            # t1 = dt.timestamp()

            self._grid.project()

            #dt = datetime.now()
            # print(dt.timestamp()-t1)

            self._image.draw()
            self._grid.draw()

            dt = datetime.now()
            self._t_last = dt.timestamp()
            it += 1
            if it >= int(self._args.num_iterations):
                it = 1
                epoch += 1
                self.custom_save(epoch)
                print('Epoch {0} started'.format(epoch))
                self.move_bunch(epoch)

        self._loop = self._window.after(1, self._run_once)

    def add_bunch(self, pose):
        xs = pose[0]
        ys = pose[1]
        return self._add_points(zip(xs, ys))

    def _add_points(self, xys, visible=True):
        new_handles = OrderedDict()
        if visible:
            for ptx, pty in xys:
                h_id = self._image.create_handle_nocheck(ptx, pty)
                # it would never be -1 if nocheck method is used
                if h_id != -1:
                    new_handles[h_id] = (ptx, pty)
            foundmask = self._grid.create_bunch_cp(new_handles=new_handles)
        else:
            for i, [ptx, pty] in enumerate(xys):
                new_handles[i] = (ptx, pty)
            foundmask = self._grid.create_bunch_cp(new_handles=new_handles)

        for k, f in zip(list(new_handles.keys()), foundmask):
            if not f:
                self._image.remove_handle(k)
                del new_handles[k]
        print(foundmask)
        return (new_handles, foundmask)

    def _add_border_points(self, num_points=5, visible=False):
        if self._image._borders is not None:
            for i, border in enumerate(self._image._borders):
                points_ind = list(map(int, np.linspace(0, border.shape[0] - 1, num_points)))
                self._add_points(border[points_ind][:, [1,0]], visible=visible)

    def select_handle(self, e):
        handle_id = self._image.select_handle(e.x, e.y)

        if handle_id == -1:
            handle_id = self._image.create_handle(e.x, e.y)
            if handle_id != -1:
                if not self._grid.create_control_point(handle_id, e.x, e.y):
                    self._image.remove_handle(handle_id)
                    return False
            else:
                return False

        self._active_handle = handle_id
        return True

    def deselect_handle(self, e):
        self._active_handle = -1

    def remove_handle(self, e):
        handle_id = self._image.select_handle(e.x, e.y)
        if handle_id != -1:
            self._grid.remove_control_point(handle_id)
            self._image.remove_handle(handle_id)

    def move_handle(self, e):
        if self._active_handle != -1:
            self._image.move_handle(self._active_handle, e.x, e.y)
            self._grid.set_control_target(self._active_handle, e.x, e.y)

    def move_bunch(self, num):
        newpos = self._smoothed[num]
        xs = newpos[0][self._foundmask]
        ys = newpos[1][self._foundmask]
        i = 0
        for h_id, h_obj in self._handles.items():
            self._image.move_handle(h_id, xs[i], ys[i])
            self._grid.set_control_target(h_id, xs[i], ys[i])
            i += 1

    def morph_refresh(self):
        morph_path = self._args.morph_path
        start = self._args.morphing_start_frame
        stop = self._args.morphing_end_frame
        if stop == -1:
            pass

        morph_image_paths = os.listdir(morph_path)
        files_to_set = list(map(int, np.linspace(0, len(morph_image_paths), stop - start)))

        while True:
            if not start <= epoch <= stop:
                yield
                continue
            new_image = np.array(Image.open())
