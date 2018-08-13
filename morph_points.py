from classes.Masker import Masker
import cv2
import numpy as np


def preprocess(im, masker, size=[0, 0]):
    bbox = masker.bounding_box(numpy=True)
    im = im[bbox[0,0]:bbox[1,0], bbox[0,1]:bbox[1,1]] 
    masker.crop(bbox)
    if sum(size) > 0:
        coefs = np.array(im.shape[:2]) / np.array(size)
        if coefs[1] < coefs[0]: 
            size[1] = int(round(im.shape[1]/coefs[0]))
        else: 
            size[0] = int(round(im.shape[0]/coefs[1]))
        masker.scale(size[1], size[0])
        im = cv2.resize(im, tuple(size[::-1]))
    return im, masker

def get_points( from_tuple, to_tuple):
    # Takes two tuples like (im_path, mask_path)
    # Image extension is considered .png
    im_from = cv2.imread(from_tuple[0])
    masker_from = Masker(from_tuple[1])
    im_from, masker_from = preprocess(im_from, masker_from)
    
    im_to = cv2.imread(to_tuple[0])
    masker_to = Masker(to_tuple[1])
    im_to, masker_to = preprocess(im_to, masker_to, size=list(im_from.shape[:2]))
    print(im_to.shape)

    im_path, mask_path = [f.replace('.png', '_processed.png') for f in from_tuple]
    cv2.imwrite(im_path, im_from)
    masker_from.save(mask_path)
    print("Saved 'from': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))

    im_path, mask_path = [f.replace('.png', '_processed.png') for f in to_tuple]
    cv2.imwrite(im_path, im_to)
    masker_to.save(mask_path)
    print("Saved 'to': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))
    return 
    