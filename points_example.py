from morph_points import get_points

from_num = '2'
to_num = '1'
dir = 'morphing/'

get_points((dir+'{}.png'.format(from_num), dir+'m{}.png'.format(from_num), dir+'{}_keypoints.json'.format(from_num)),
           (dir+'{}.png'.format(to_num),dir+'m{}.png'.format(to_num), dir+'{}_keypoints.json'.format(to_num)),
           contour_pairs=True)
