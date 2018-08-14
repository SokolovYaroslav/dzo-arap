#!/bin/bash

make && python main.py --path assets/frames/middle_greetings/1.png \
                       --mask masks/1_new_full_mask.png \
                       --keypoints_dir assets/frames/middle_greetings_jsons \
                       --visible_bodypart_points True \
                       --num_bodypart_points 5 \
                       --bodyparts_box_sizes 32,25,32,32,32 \
                       --num_iterations 25 \
                       --grid True --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000
