import numpy as np
from PIL import Image, ImageTk
import cv2
import os
from classes.Masker import Masker

class ImageHelper:
    """
    Manipulates directly with image.
    Ensures it's loading, updating and redrawing as well as provides info about loaded image.
    """

    """ radius of visual representation of control point """
    HANDLE_RADIUS = 5

    def __init__(self, cw, args, gui = True):
        self.BINDER_MASK_THRESHOLD = args.bodypart_thresh
        self.cw = cw
        self._canvas = None

        self._im_obj = Image.open(args.path)
        if gui:
            self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # keeping reference for image to load

        self._size = self._im_obj.size
        self._pos = (self.width/2, self.height/2)

        self._orig = np.array(self._im_obj)  # original data of the image immediately after load
        self._data = np.array(self._im_obj)  # current data of the image to draw

        self._masker = None
        self._mask = None
        if args.mask is not None:
            self._masker = Masker(mask_path=args.mask)
            self._mask = self._masker.whole_mask
        else:
            self._compute_mask()
            self._masker = Masker(mask=self._mask)
            self._mask = self._masker.whole_mask
        if args.save_mask:
            dir = os.path.dirname(args.path).replace('assets', 'masks')
            if not os.path.exists(dir):
                os.mkdir(dir)
                print("Created directory", dir)
            path = args.path.replace('assets', 'masks')
            self._masker.save(path)

        self._borders = None
        self.compute_background(args)

        self._handles = set()

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, canvas):
        self._canvas = canvas

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def mask(self):
        return self._mask

    @property
    def cmask(self):
        """
        :return: Object for communicating with C interface for image mask
        """
        return self._mask

    @property
    def cdata(self):
        """
        :return: Object for communicating with C interface for current image data
        """
        if self._data.dtype is not np.uint8:
            self._data = self._data.astype(np.uint8)
        return self._data

    @property
    def corig(self):
        """
        :return: Object for communicating with C interface for data of original image
        """
        if self._orig.dtype is not np.uint8:
            self._orig = self._orig.astype(np.uint8)
        return self._orig

    def compute_background(self, args):
        def get_binder_mask(part_mask, body_mask, bodypart: str):
            part_coords =  np.argwhere(part_mask)
            full_mask = part_mask + body_mask

            body_cont = self._masker.get_contour("body")
            full_cont = self._masker.get_contour(["body", bodypart])

            #KOSTYL: set(body_cont) - set(full_cont)
            tmp_cont = np.zeros_like(full_mask, dtype=np.bool)
            tmp_cont[body_cont[:, 0], body_cont[:, 1]] = True
            tmp_cont[full_cont[:, 0], full_cont[:, 1]] = False

            border = np.argwhere(tmp_cont)

            #shape: (num border points, num part_coords)
            part_dists = np.sqrt((border ** 2).sum(axis=1, keepdims=1) + (part_coords ** 2).sum(axis=1) \
                                -2 * border.dot(part_coords.T)).sum(axis=0)
            #map to [0,1]
            part_dists = (part_dists - part_dists.min())
            part_dists /= part_dists.max()

            binder_coords = part_coords[part_dists < self.BINDER_MASK_THRESHOLD, :]
            binder_mask = np.zeros_like(part_mask, dtype=np.bool)
            binder_mask[binder_coords[:, 0], binder_coords[:, 1]] = True
            return binder_mask, border

        if args.background_color is not None:
            self._background = np.zeros_like(self._orig) + args.background_color
        elif args.background is not None:
            self._background = np.array(Image.open(args.background))
            print(self._background.shape, self._orig.shape)
            diff0 = self._background.shape[0] - self._orig.shape[0]
            diff1 = self._background.shape[1] - self._orig.shape[1]
            if diff0 != 0:
                self._background = self._background[diff0//2:-diff0//2,:,:]
            if diff1 != 0:
                self._background = self._background[:,diff1//2:-diff1//2,:]
            print(self._background.shape)
            assert self._background.shape == self._orig.shape
        else:
            self._background = self._orig * (1 - self._mask[:, :, np.newaxis])
        #######################
        #TODO: SOME INPAINTING#
        #######################
        if len(self._masker.segmented_body_parts()) != 0 and args.split_body_on_parts:
            self._borders = []
            body_mask = self._masker.mask2bool(self._masker.body_mask)
            body_aug_mask = body_mask.copy()
            parts_mask = np.zeros_like(body_mask, dtype=np.bool)
            for part in self._masker.segmented_body_parts():
                part_mask = self._masker.mask2bool(self._masker.get_mask(part))
                parts_mask += part_mask
                binder_mask, border = get_binder_mask(part_mask, body_mask, part)
                body_aug_mask += binder_mask
                if border[:, 0].max() - border[:, 0].min() > border[:, 1].max() - border[:, 1].min():
                    indicies = border[:,0].argsort()
                else:
                    indicies = border[:,1].argsort()
                border = border[indicies]
                self._borders.append(border)
            self._background[body_aug_mask] = self._orig[body_aug_mask]
            self._mask = parts_mask
        

        
    def _compute_mask(self):
        """ Compute mask of image - foreground is True, background is False """
        self._mask = np.full((self.height, self.width), True, dtype=np.bool)
        self.cw.mask(self._mask, self._orig, self.width, self.height, 10)

    def _update(self):
        """ Create new image from current data """
        self._im_obj = Image.fromarray(self._data)  # putdata(self._data)
        self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # need to keep reference for image to load

    def draw(self):
        """ Redraw image from associated data """
        self._update()

        self._canvas.delete("IMAGE")
        self._canvas.create_image(self._pos, image=self._tk_obj, tag="IMAGE")

        for h in self._handles:
            self._canvas.tag_raise(h)

        return True

    def create_handle(self, x, y):
        """
        Creates handle at given position if it doesn't exist yet
        :return: Handle ID or -1 if creation failed due to overlap with existing one
        """
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)

        overlap = self._canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3])
        for obj_id in overlap:
            if obj_id in self._handles:
                return -1

        handle_id = self._canvas.create_oval(bbox, fill="blue", outline="blue", tag="HANDLE")
        self._handles.add(handle_id)
        return handle_id

    def create_handle_nocheck(self, x, y):
        bbox = (x - self.HANDLE_RADIUS, y - self.HANDLE_RADIUS,
                x + self.HANDLE_RADIUS, y + self.HANDLE_RADIUS)
        handle_id = self._canvas.create_oval(bbox, fill="blue", outline="blue", tag="HANDLE")
        self._handles.add(handle_id)
        return handle_id


    def select_handle(self, x, y):
        """
        Checks if there is handle at given position
        :return: Handle ID if handle at position exists, -1 otherwise
        """
        overlap = self._canvas.find_overlapping(x, y, x, y)
        for obj_id in overlap:
            if obj_id in self._handles:
                return obj_id

        return -1

    def move_handle(self, handle_id, x, y):
        """ Change position of given handle """
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)
        self._canvas.coords(handle_id, bbox)

    def remove_handle(self, handle_id):
        """ Removes handle """
        self._canvas.delete(handle_id)
        self._handles.remove(handle_id)

    def clear(self, pixel=np.array([0, 0, 0])):
        if self._background is not None:
            self._data[:, :, :] = self._background
            return
        self._data[:, :] = pixel
