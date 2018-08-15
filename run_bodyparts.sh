#!/bin/bash

make && python main.py --path assets/frames/slow_raise/1.png \
                       --background_color 128,128,128 \
                       --mask masks/handwave_mask.png \
                       --background assets/tomswallpapers.com-27225.jpg \
                       --keypoints_dir assets/frames/slow_raise_jsons \
                       --visible_bodypart_points True \
                       --num_bodypart_points 5 \
                       --bodyparts_box_sizes 32,25,25,32,32 \
                       --num_iterations 25 \
                       --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000 \
                       --bodypart_thresh 0 \
                       --outdir slowrase_noback/
