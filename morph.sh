#!/bin/bash

#DIR=./morphing
DIR=./morphing
#MORPH_DIR=../image_morphing/build
MORPH_DIR=../image_morphing/build

from='4'
to='1'

echo "-------Preparing files and points------"
python $DIR/../morph_points.py $DIR/${from}.png $DIR/m${from}.png $DIR/${from}_keypoints.json \
                               $DIR/${to}.png $DIR/m${to}.png $DIR/${to}_keypoints.json

echo "-------Calculating morphing-------"
$MORPH_DIR/image_morphing $DIR/${from}_processed.png $DIR/${from}.txt $DIR/${to}_processed.png $DIR/${to}.txt $DIR/out

echo "-------Making a gif-------"
convert   -delay 0.5   -loop 0   $DIR/out/{0..99}.jpg   $DIR/${from}_to_${to}.gif

