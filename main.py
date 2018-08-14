from classes.Application import Application
import argparse


def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


parser = argparse.ArgumentParser()
parser.add_argument("--mask", default=None, help="custom mask path")
parser.add_argument("--box_size", default=32, type=int, help="box size for grid")
parser.add_argument("--keypoints_dir", help="path to keypoints directory")
parser.add_argument("--path", default="assets/sokolov_228.jpg", help="path to image")
parser.add_argument("--grid", default=False, type=str2bool, help="to show grid pass True")
parser.add_argument("--save_mask", default=str2bool, help="to save computed mask into masks/")
parser.add_argument("--num_iterations", default=50, type=int, help="number of iterations to fit each pose")
parser.add_argument(
    "--enumerate",
    default=False,
    type=str2bool,
    help="to automatically enumerate paths for saving deformed images",
)
parser.add_argument(
    "--control_weight", default=100000, type=int, help="control weight for grid"
)

app = Application(parser.parse_args())

app.bind("<Button-1>", app.select_handle)
app.bind("<ButtonRelease-1>", app.deselect_handle)
app.bind("<Button-3>", app.remove_handle)
app.bind("<B1-Motion>", app.move_handle)

app.run()
