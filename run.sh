#!/bin/bash

make && python main.py --path assets/sokolov_228.jpg \
                       --grid False --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000 \
                       --keypoints assets/sokolov_228_keypoints.json #--mask ...
