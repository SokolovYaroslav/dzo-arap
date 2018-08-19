#!/bin/bash

#DIR=./morphing
DIR=./morphing

from='4'
to='3'
num_frames='100'

echo "-------Preparing files and points------"
python $DIR/../morph_points.py $DIR/${from}.png $DIR/m${from}.png $DIR/${from}_keypoints.json \
                               $DIR/${to}.png $DIR/m${to}.png $DIR/${to}_keypoints.json

echo "-------Calculating morphing-------"
mkdir $DIR/out_${from}_${to}
$DIR/../image_morphing $DIR/${from}_processed.png $DIR/${from}.txt $DIR/${to}_processed.png \
                       $DIR/${to}.txt ${num_frames} $DIR/out_${from}_${to}

echo "-------Making a gif-------"
convert   -delay 0.5   -loop 0   $DIR/out_${from}_${to}/{0..99}.jpg   $DIR/${from}_to_${to}.gif

