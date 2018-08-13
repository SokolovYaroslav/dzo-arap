#!/bin/bash

make && python main.py --path assets/masked_001.png \
                       --mask masks/001_full_mask.png \
                       --visible_bodypart_points True \
                       --num_bodypart_points 5 \
                       --grid True --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000
