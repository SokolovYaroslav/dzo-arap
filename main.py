from classes.Application import Application
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mask", default=None, help="custom mask path")
parser.add_argument("--path", default="assets/sokolov_228.jpg", help="path to image")
parser.add_argument("--grid", default=False, help="to show grid pass True")
parser.add_argument(
    "--keypoints", default="assets/sokolov_228_keypoints.json", help="path to keypoints"
)
parser.add_argument(
    "--save_mask", default=False, help="to save computed mask into masks/"
)
parser.add_argument(
    "--enumerate",
    default=False,
    help="to automatically enumerate paths for saving deformed images",
)

app = Application(parser.parse_args())

app.bind("<Button-1>", app.select_handle)
app.bind("<ButtonRelease-1>", app.deselect_handle)
app.bind("<Button-3>", app.remove_handle)
app.bind("<B1-Motion>", app.move_handle)

app.run()
