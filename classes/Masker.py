from classes.utils import get_pose
import cv2
import os
import numpy as np
import sys


class Masker:
    PARTS = ["head", "left_leg", "right_leg", "left_arm", "right_arm"]
    COLORS = dict()
    for i in range(len(PARTS)):
        COLORS[PARTS[i]] = 50 * (i + 1)

    def __init__(self, mask_path=None, keypoints_path=None, mask=None):
        self._mask_path = mask_path
        self._mask_im = None
        self.whole_mask = None
        self.body_mask = None
        self.parts_masks = dict()

        if self._mask_path is not None:
            self._mask_im = cv2.imread(self._mask_path)  # TODO: check if success
            print(self._mask_path)
            self._mask_init()
        elif mask is not None:
            self.whole_mask = mask
            self._mask_im = mask.copy()
        else:
            print("Mask.py: Provide either mask as np.array, or path to mask")
            sys.exit(1)

        if keypoints_path is not None:
            self.keypoints = get_pose(keypoints_path, with_face=True, with_hands=True)
            print("Initialize masker with keypoints. Shape:", self.keypoints.shape)

    def _mask_init(self):
        self.whole_mask = self.mask2bool(self._mask_im[:, :, 0])
        if self.is_binary(self._mask_im):
            return
        self.body_mask = self.mask2bool(self._mask_im[:, :, 1])
        for part in self.PARTS:
            part_mask = self._mask_im[:, :, 2] == self.COLORS[part]
            if part_mask.sum() > 0:
                self.parts_masks[part] = part_mask

    def is_segmented(self):
        return self.is_binary(self._mask_im)

    def is_binary(self, mask):
        # Check whether the layers are the same
        # TODO: more sophisticated method
        if len(mask.shape) == 2:
            return True
        diff1 = mask[:, :, 1] ^ mask[:, :, 0]
        diff2 = mask[:, :, 2] ^ mask[:, :, 0]
        return diff1.sum() + diff2.sum() == 0

    def segmented_body_parts(self):
        return self.parts_masks.keys()

    def save(self, path):
        return cv2.imwrite(path, self._mask_im * (255 / np.max(self._mask_im)))

    def get_mask(self, part_name):
        if part_name in self.parts_masks:
            return self.parts_masks[part_name]
        elif part_name == "whole" or part_name == "all":
            return self.whole_mask
        elif part_name == "body":
            return self.body_mask
        else:
            return None

    def get_contour(self, parts=["whole"], continious=True):
        # TODO: support getting mask & contour for deformed image
        # if part not in ["whole", "body", "all"] and \
        #   part not in self.segmented_body_parts():
        #    print("Can't get contour for {}. No such body part found.".format(part))
        #    return None
        if type(parts) != list:
            parts = [parts]
        mask = sum([self.get_mask(part).astype(np.uint8) for part in parts])
        mask = np.clip(mask, 0, 1)

        chain_approx_method = (
            cv2.CHAIN_APPROX_NONE if continious else cv2.CHAIN_APPROX_SIMPLE
        )
        im2, contours, hierarchy = cv2.findContours(
            mask * 255, cv2.RETR_TREE, chain_approx_method
        )
        cont_ind = np.argmax(np.array([cont.shape[0] for cont in contours]))
        contour = contours[cont_ind].reshape(-1, 2)[:, [1, 0]]
        return contour

    def bounding_box(self, part="whole", numpy=True):
        # [y0, x0, y1, x1] Note: y is counted from the top
        contour = np.array(self.get_contour(part))
        res = [
            np.min(contour[:, 0]),
            np.min(contour[:, 1]),
            np.max(contour[:, 0]),
            np.max(contour[:, 1]),
        ]
        if numpy:
            res = np.array(res).reshape(2, 2)
        return res

    def _center(self):
        bbox = self.bounding_box()
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

    def crop(self, box, numpy=True):
        if not numpy:
            box = np.array(box).reshape(2, 2)
        self._mask_im = self._mask_im[box[0, 0] : box[1, 0], box[0, 1] : box[1, 1]]
        self._mask_init()

        if self.keypoints is not None:
            self.keypoints = self.keypoints - box[0]
            self.keypoints[:, 0] = np.clip(
                self.keypoints[:, 0], 0, box[1, 0] - box[0, 0] - 1
            )
            self.keypoints[:, 1] = np.clip(
                self.keypoints[:, 1], 0, box[1, 1] - box[0, 1] - 1
            )

    def scale(self, width, height):
        prev_shape = self._mask_im.shape[:2]
        self._mask_im = cv2.resize(
            self._mask_im.astype(np.uint8) * 255, (width, height)
        )
        self._mask_im = self.mask2bool(self._mask_im)
        self._mask_init()
        if self.keypoints is not None:
            self.keypoints[:, 0] = self.keypoints[:, 0] * (height / prev_shape[0])
            self.keypoints[:, 1] = self.keypoints[:, 1] * (width / prev_shape[1])

    def mask2bool(self, mask):
        # TODO: more sophisticated method
        return mask.astype(np.bool)
