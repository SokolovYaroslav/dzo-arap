import numpy as np
import os
import json


def get_pose(kpts_path, with_hands=True, with_face=True):
    with open(os.path.join(kpts_path), "r") as f:
        res = json.load(f)
    cur_pose = np.array(res["people"][0]["pose_keypoints_2d"])
    points = cur_pose.reshape(-1, 3)[:, [1, 0]]

    if with_hands:
        l_hand = res["people"][0]["hand_left_keypoints_2d"]
        r_hand = res["people"][0]["hand_right_keypoints_2d"]
        l_hand = np.array(l_hand).reshape(-1, 3)[:, [1, 0]]
        r_hand = np.array(r_hand).reshape(-1, 3)[:, [1, 0]]
        points = np.concatenate((points, l_hand, r_hand))

    if with_face:
        face = res["people"][0]["face_keypoints_2d"]
        if len(face) > 0:
            face = np.array(face).reshape(-1, 3)[:, [1, 0]]
            points = np.concatenate((points, face))
    return points
