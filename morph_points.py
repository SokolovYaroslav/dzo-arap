from classes.Masker import Masker
import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform, euclidean

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


def get_points(from_tuple, to_tuple, shuffle=True):
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

    pairs = calculate_close_pairs(cont_from, cont_to, (im_from.shape[:2], im_to.shape[:2]))
    if shuffle:
        np.random.shuffle(pairs)
    from_pts, to_pts = from_tuple[0].replace('.png', '.txt'), to_tuple[0].replace('.png', '.txt')
    #print("Saving points into {}: {} and {}".format(out_dir, from_pts, to_pts))
    with open(from_pts, 'w') as f:
        for i in range(pairs.shape[0]):
            f.write("{} {}\n".format(pairs[i, 1], pairs[i, 0]))
    with open(to_pts, 'w') as f:
        for i in range(pairs.shape[0]):
            f.write("{} {}\n".format(pairs[i, 3], pairs[i, 2]))
    return pairs


def calculate_close_pairs(pts1, pts2, shapes):
    pts1_sort = contour_way(pts1)
    pts2_sort = contour_way(pts2)
    upper_point = pts1_sort[np.argmax(pts1_sort, axis=0)[1]]
    dists = [euclidean(upper_point, p) for p in pts2_sort]
    min_dist = np.argmin(dists)
    pts2_sort = pts2_sort[min_dist:] + pts2_sort[:min_dist]

    # Scale points back
    shape_from, shape_to = shapes[0], shapes[1]
    def scale_back(point):
        if shape_from[0] == shape_to[0]:
            # differ in 1st, i.e. width
            point[0] = point[0]*shape_to[0]/shape_from[0]
            point[0] += np.abs(shape_to[0] - shape_from[0]) / 2
        else:
            point[1] = point[1]*shape_to[1]/shape_from[1]
            point[1] += np.abs(shape_to[1] - shape_from[1]) / 2
        return point

    pts2_sort = np.apply_along_axis(scale_back, 0, pts2_sort)
    sz = min(len(pts1_sort), len(pts2_sort))
    res = np.concatenate((pts1_sort[:sz], pts2_sort[:sz]), axis=1)
    return res

def contour_way(points):
    dists = squareform(pdist(np.concatenate((points, points))))
    dists = dists[:points.shape[0], :points.shape[0]]
    min_arg_dists = np.argsort(dists, axis=1)
    used = [False for _ in range(len(points))]
    cur_p = 0
    res = []
    for _ in range(len(points)):
        used[cur_p] = True
        res.append(points[cur_p])
        for next_p in min_arg_dists[cur_p, :]:
            if not used[next_p]:
                cur_p = next_p
                break
    return res