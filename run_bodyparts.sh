#!/bin/bash

make && python main.py --path assets/masked_001.png \
                       --mask assets/mask0.png \
                       --bodypart_mask assets/mask0_hands.png \
                       --grid False --save_mask False --enumerate True \
                       --box_size 32 --control_weight 100000
