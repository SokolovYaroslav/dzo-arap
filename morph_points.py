from classes.Masker import Masker
import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform


def preprocess(im, masker, size=[0, 0]):
    bbox = masker.bounding_box(numpy=True)
    im = im[bbox[0, 0] : bbox[1, 0], bbox[0, 1] : bbox[1, 1]]
    masker.crop(bbox)
    if sum(size) > 0:
        prev_size = [size[0], size[1], 3]
        offset = [0, 0]
        coefs = np.array(im.shape[:2]) / np.array(size)
        if coefs[1] < coefs[0]:
            # then change width, height stays the same
            prev_width = size[1]
            size[1] = int(round(im.shape[1] / coefs[0]))
            offset[1] = np.abs(int((size[1] - prev_size[1]) / 2))
        else:
            size[0] = int(round(im.shape[0] / coefs[1]))
            offset[0] = np.abs(int((size[0] - prev_size[0]) / 2))
        masker.scale(size[1], size[0])
        im = cv2.resize(im, tuple(size[::-1]))
        new_im = np.zeros(tuple(prev_size))
        new_im[offset[0] : offset[0] + size[0], offset[1] : offset[1] + size[1]] = im
        im = new_im
    return im, masker


def get_points(from_tuple, to_tuple):
    # Takes two tuples like (im_path, mask_path)
    # Image extension is considered .png
    im_from = cv2.imread(from_tuple[0])
    masker_from = Masker(from_tuple[1])
    im_from, masker_from = preprocess(im_from, masker_from)

    im_to = cv2.imread(to_tuple[0])
    masker_to = Masker(to_tuple[1])
    im_to, masker_to = preprocess(im_to, masker_to, size=list(im_from.shape[:2]))
    print(im_to.shape)

    im_path, mask_path = [f.replace(".png", "_processed.png") for f in from_tuple]
    cv2.imwrite(im_path, im_from)
    masker_from.save(mask_path)
    print("Saved 'from': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))

    im_path, mask_path = [f.replace(".png", "_processed.png") for f in to_tuple]
    cv2.imwrite(im_path, im_to)
    masker_to.save(mask_path)
    print("Saved 'to': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))

    masker_to.scale(im_from.shape[1], im_from.shape[0])
    cont_from = masker_from.get_contour(continious=False)
    cont_to = masker_to.get_contour(continious=False)

    return calculate_close_pairs(cont_from, cont_to)


def calculate_close_pairs(pts1, pts2):
    all_pts = np.concatenate((pts1, pts2))
    dist = squareform(pdist(all_pts))

    inf = np.max(dist) + 1
    dist[: pts1.shape[0], : pts1.shape[0]] = inf
    dist[pts1.shape[0] :, pts1.shape[0] :] = inf

    indices = np.argmin(dist, axis=0)
    if pts1.shape[0] < pts2.shape[0]:
        res = np.concatenate((pts1, all_pts[indices[: pts1.shape[0]]]), axis=1)
    else:
        res = np.concatenate((pts2, all_pts[indices[pts1.shape[0] :]]), axis=1)
    return res
