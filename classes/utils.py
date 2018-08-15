import numpy as np
import os
import json


def get_poses(kpts_dir, with_hands=False, interpolate_hands=False):
    kpt_files = os.listdir(kpts_dir)
    kpt_files.sort(key=lambda e: int(e.split('_')[0]))
    poses = []
    for file in kpt_files:
        with open(os.path.join(kpts_dir, file), 'r') as f:
            res = json.load(f)
        cur_pose = res['people'][0]['pose_keypoints_2d']
        xs = cur_pose[::3]
        ys = cur_pose[1::3]
        if with_hands:
            l_hand = res['people'][0]['hand_left_keypoints_2d']
            r_hand = res['people'][0]['hand_right_keypoints_2d']
            # appending 12'th point, located on the end of middle finger
            xs.append(l_hand[33])
            ys.append(l_hand[34])
            xs.append(r_hand[33])
            ys.append(r_hand[34])
        if interpolate_hands:
            xs.append((xs[2] + xs[3]) / 2)
            xs.append((xs[3] + xs[4]) / 2)
            xs.append((xs[5] + xs[6]) / 2)
            xs.append((xs[6] + xs[7]) / 2)

            ys.append((ys[2] + ys[3]) / 2)
            ys.append((ys[3] + ys[4]) / 2)
            ys.append((ys[5] + ys[6]) / 2)
            ys.append((ys[6] + ys[7]) / 2)


        poses.append([xs, ys])
    return np.array(poses)

def smooth_poses(poses, win_length):
    smoothed = []
    for i in range(poses.shape[0] - win_length):
        slc = poses[i:i+win_length, :]
        smoothed.append(slc.sum(axis=0)/win_length)
    return np.array(smoothed)