from classes.Masker import Masker
from classes.utils import get_pose
import cv2
import numpy as np
from scipy.spatial.distance import pdist, squareform, euclidean
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
        masker.keypoints = masker.keypoints + np.array(offset)
        im = new_im
    return im, masker, size


def get_points(from_tuple, to_tuple, include_edge_points=True, step=1, contour_pairs=False):
    # Takes two tuples like (im_path, mask_path, kpts_path)
    # Image extension is considered .png
    im_from = cv2.imread(from_tuple[0])
    masker_from = Masker(
        from_tuple[1], keypoints_path=from_tuple[2] if len(from_tuple) == 3 else None
    )
    im_from, masker_from, _ = preprocess(im_from, masker_from)

    im_to = cv2.imread(to_tuple[0])
    masker_to = Masker(
        to_tuple[1], keypoints_path=to_tuple[2] if len(to_tuple) == 3 else None
    )
    im_to, masker_to, to_shape = preprocess(
        im_to, masker_to, size=list(im_from.shape[:2])
    )

    im_path, mask_path, _ = [f.replace(".png", "_processed.png") for f in from_tuple]
    cv2.imwrite(im_path, im_from)
    masker_from.save(mask_path)
    print("Saved 'from': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))

    im_path, mask_path, _ = [f.replace(".png", "_processed.png") for f in to_tuple]
    cv2.imwrite(im_path, im_to)
    masker_to.save(mask_path)
    print("Saved 'to': \n\timage into {}\n\tmask into {}".format(im_path, mask_path))

    if len(from_tuple) == 3 and len(to_tuple) == 3:
        kpts_from = masker_from.keypoints
        kpts_to = masker_to.keypoints
        kpts = np.concatenate((kpts_from, kpts_to), axis=1).astype(int)
        pairs = kpts

    masker_to.scale(im_from.shape[1], im_from.shape[0])
    cont_from = masker_from.get_contour(continious=True)
    cont_to = masker_to.get_contour(continious=True)

    if contour_pairs:
        contour_pairs = calculate_close_pairs(
            cont_from, cont_to, (im_from.shape[:2], to_shape[:2])
        )
        contour_pairs = contour_pairs[::step, :]
        pairs = np.concatenate((pairs, contour_pairs))

    img_p_from = draw_points(im_from, pairs[:, [1, 0]], step=3)
    img_p_to = draw_points(im_to, pairs[:, [3, 2]], step=3)
    cv2.imwrite(from_tuple[0].replace('.png', '_points.png'), img_p_from)
    cv2.imwrite(to_tuple[0].replace('.png', '_points.png'), img_p_to)

    height, width = im_from.shape[:2]
    corners = np.array([[0, 0], [0, width-1], [height-1, 0], [height-1, width-1]]).astype(int)
    sides = np.array([[height / 2, 0], [height / 2, width-1], [0, width / 2], [height - 1, width / 2]]).astype(int)
    edge_points = np.concatenate((corners, sides))
    edge_points = np.repeat(edge_points, 2, axis=1)[:,[0,2,1,3]]
    if include_edge_points:
        height, width = im_from.shape[:2]
        corners = np.array(
            [[0, 0], [0, width - 1], [height - 1, 0], [height - 1, width - 1]]
        ).astype(int)
        sides = np.array(
            [
                [height / 2, 0],
                [height / 2, width - 1],
                [0, width / 2],
                [height - 1, width / 2],
            ]
        ).astype(int)
        edge_points = np.concatenate((corners, sides))
        edge_points = np.repeat(edge_points, 2, axis=1)[:, [0, 2, 1, 3]]
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
    pts1_sort = contour_way(np.array(pts1))
    pts2_sort = contour_way(np.array(pts2))

    upper_point_pos = np.argmax(pts1_sort, axis=0)[1]
    upper_point = pts1_sort[upper_point_pos]
    dists = [euclidean(upper_point, p) for p in pts2_sort]
    min_dist = np.argmin(dists)
    pts1_sort = pts1_sort[upper_point_pos:] + pts1_sort[:upper_point_pos]
    pts2_sort = pts2_sort[min_dist:] + pts2_sort[:min_dist]

    left_point_pos = np.argmin(pts1_sort, axis=0)[0]
    left_point = pts1_sort[left_point_pos]
    right_point_pos = np.argmax(pts1_sort, axis=0)[0]
    dists = [euclidean(left_point, p) for p in pts2_sort]
    if dists[left_point_pos] > dists[right_point_pos]:
        pts2_sort = pts2_sort[::-1]
        pts2_sort = [pts2_sort[0]] + pts2_sort[:-1]

    pts1_sort, pts2_sort = regulirize_length(pts1_sort, pts2_sort)

    # Scale points back
    shape_from, shape_to = shapes[0], shapes[1]
    # print("Scale from {} to {}".format(shape_from, shape_to))    
    def scale_back(point):
        if shape_from[1] == shape_to[1]:
            point[0] += (shape_from[0] - shape_to[0]) / 2
            point[0] = point[0] * (shape_to[0] / shape_from[0])
        else:
            point[1] = point[1] * (shape_to[1] / shape_from[1])
            point[1] += (shape_from[1] - shape_to[1]) / 2
        return point

    pts2_sort = np.apply_along_axis(scale_back, 1, pts2_sort)
    res = np.concatenate((pts1_sort, pts2_sort), axis=1)
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
        for p in min_arg_dists[cur_p]:
            if not used[p]:
                cur_p = p
                break
    return res

def regulirize_length(pts1, pts2):
    swap = False
    if len(pts2) < len(pts1):
        swap = True
        pts1, pts2 = pts2, pts1
    pts2 = pts2 + pts2[:100] 
    pts2_new = []
    i = 0
    for p in pts1:
        dists = [euclidean(p, _p) for _p in pts2[i:i + 100]]
        i_new = i + np.argmin(dists)
        pts2_new.append(pts2[i_new])
        i = i_new + 1
    return (pts2_new, pts1) if swap else (pts1, pts2_new)

def draw_points(img, points, step=1):
    img = img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (255, 255, 255)
    draw_point = lambda img, p, i: cv2.putText(img, str(i), p, font, 0.3, color, 1, cv2.LINE_AA)
    for i in range(len(points[::step])):
        draw_point(img, (points[i * step][0], points[i * step][1]), i + 1)
    return img

if __name__ == "__main__":
    # print("Running get_points() on", sys.argv[1:])
    get_points(
        (sys.argv[1], sys.argv[2], sys.argv[3]), (sys.argv[4], sys.argv[5], sys.argv[6])
    )
