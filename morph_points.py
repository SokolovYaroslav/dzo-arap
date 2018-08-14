from classes.Masker import Masker
import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform
import sys


def preprocess(im, masker, size=[0, 0]):
    bbox = masker.bounding_box(numpy=True)
    im = im[bbox[0, 0] : bbox[1, 0], bbox[0, 1] : bbox[1, 1]]
    masker.crop(bbox)
    if sum(size) > 0:
        prev_size = [size[0], size[1], 3]
        offset = [0, 0]
        coefs = np.array(im.shape[:2]) / np.array(size)
        real_shape = size.copy()
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
    return im, masker, size


def get_points(from_tuple, to_tuple, shuffle=True, include_edge_points=True):
    # Takes two tuples like (im_path, mask_path)
    # Image extension is considered .png
    im_from = cv2.imread(from_tuple[0])
    masker_from = Masker(from_tuple[1])
    im_from, masker_from, _ = preprocess(im_from, masker_from)

    im_to = cv2.imread(to_tuple[0])
    masker_to = Masker(to_tuple[1])
    im_to, masker_to, to_shape = preprocess(
        im_to, masker_to, size=list(im_from.shape[:2])
    )
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

    pairs = calculate_close_pairs(cont_from, cont_to, (im_from.shape[:2], to_shape[:2]))
    if shuffle:
        np.random.shuffle(pairs)

    height, width = im_from.shape[:2]
    corners = np.array([[0, 0], [0, width-1], [height-1, 0], [height-1, width-1]]).astype(int)
    sides = np.array([[height / 2, 0], [height / 2, width-1], [0, width / 2], [height - 1, width / 2]]).astype(int)
    edge_points = np.concatenate((corners, sides))
    edge_points = np.repeat(edge_points, 2, axis=1)[:,[0,2,1,3]]
    if include_edge_points:
        pairs = np.concatenate((edge_points, pairs))

    from_pts, to_pts = (
        from_tuple[0].replace(".png", ".txt"),
        to_tuple[0].replace(".png", ".txt"),
    )
    print("Saving points into: {} and {}".format(from_pts, to_pts))
    with open(from_pts, "w") as f:
        for i in range(pairs.shape[0]):
            f.write("{} {} \n".format(pairs[i, 1], pairs[i, 0]))
    with open(to_pts, "w") as f:
        for i in range(pairs.shape[0]):
            f.write("{} {} \n".format(pairs[i, 3], pairs[i, 2]))
    return pairs


def calculate_close_pairs(pts1, pts2, shapes):
    all_pts = np.concatenate((pts1, pts2))
    dist = squareform(pdist(all_pts))

    inf = np.max(dist) + 1
    dist[: pts1.shape[0], : pts1.shape[0]] = inf
    dist[pts1.shape[0] :, pts1.shape[0] :] = inf

    indices = np.argmin(dist, axis=0)

    # Scale points back
    shape_from, shape_to = shapes[0], shapes[1]
    # print("Scale from {} to {}".format(shape_from, shape_to))
    def scale_back(point):
        if shape_from[1] == shape_to[1]:
            # differ in 1st, i.e. width
            point[0] += (shape_from[0] - shape_to[0]) / 2
            point[0] = point[0] * (shape_to[0] / shape_from[0])
        else:
            point[1] = point[1] * (shape_to[1] / shape_from[1])
            point[1] += (shape_from[1] - shape_to[1]) / 2
        return point

    pts2 = np.apply_along_axis(scale_back, 1, pts2)
    all_pts[pts1.shape[0] :] = pts2.copy()
    if pts1.shape[0] < pts2.shape[0]:
        res = np.concatenate((pts1, all_pts[indices[: pts1.shape[0]]]), axis=1)
    else:
        res = np.concatenate((pts2, all_pts[indices[pts1.shape[0] :]]), axis=1)
    return res


if __name__ == "__main__":
    get_points((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4]))
