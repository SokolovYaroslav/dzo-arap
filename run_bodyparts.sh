#!/bin/bash

make && python main.py --path assets/1_new.png \
                       --mask masks/1_new_full_mask.png \
                       --split_body_on_parts True \
                       --visible_bodypart_points True \
                       --num_bodypart_points 5 \
                       --bodyparts_box_sizes 16,20,28,16,16 \
                       --grid True --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000
