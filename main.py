from classes.Application import Application
import argparse


def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

def csv2dict(csv):
    box_sizes = {}
    body_parts = ["head", "right_arm", "left_arm", "right_leg", "left_leg"]
    if csv is not None:
        for body_part, box_size in zip(body_parts, list(map(int, csv.split(',')))):
            box_sizes[body_part] = box_size
        return box_sizes
    return None


parser = argparse.ArgumentParser()
parser.add_argument("--mask", default=None, help="custom mask path")
parser.add_argument("--bodypart_mask", default=None, help="bodypart mask path")
parser.add_argument("--bodypart_thresh", type=float, default=0.075, help="threshold that uses in computing bind mask")
parser.add_argument("--num_bodypart_points", type=int, default=5, help="num points that will be automatically add at borders of bodyparts")
parser.add_argument("--visible_bodypart_points", type=str2bool, default=False, help="whether show or not bodypart points")
parser.add_argument("--box_size", default=32, type=int, help="box size for grid")
parser.add_argument("--bodyparts_box_sizes", default=None, type=csv2dict, help="box sizes in follow order: head, right arm, left arm, right leg, left leg")
parser.add_argument("--keypoints_dir", default="assets/frames/greeting_jsons", help="path to keypoints directory")
parser.add_argument("--path", default="assets/frames/greeting_frames/45.png", help="path to image")
parser.add_argument("--num_iterations", default=50, help="number of iterations to fit each pose")
parser.add_argument("--grid", default=False, type=str2bool, help="to show grid pass True")
parser.add_argument("--save_mask", default=str2bool, help="to save computed mask into masks/")
parser.add_argument(
    "--enumerate",
    default=False,
    type=str2bool,
    help="to automatically enumerate paths for saving deformed images",
)
parser.add_argument(
    "--control_weight", default=100000, type=int, help="control weight for grid"
)
parser.add_argument("--morph_path", default=None, help="path to morphing frames")
parser.add_argument("--morphing_start_frame", default=0, help="TODO:meh")
parser.add_argument("--morphing_end_frame", default=-1, help="pass -1 for last frame")

app = Application(parser.parse_args())

app.bind("<Button-1>", app.select_handle)
app.bind("<ButtonRelease-1>", app.deselect_handle)
app.bind("<Button-3>", app.remove_handle)
app.bind("<B1-Motion>", app.move_handle)

app.run()
