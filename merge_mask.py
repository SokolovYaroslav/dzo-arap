import cv2
import numpy as np
import argparse
import os

# In --in_dir must lay 6 png masks:
# body.png, head.png, left_leg.png, right_leg.png, left_arm.png, right_arm.png

parser = argparse.ArgumentParser()
parser.add_argument("--in_dir", required=True)
parser.add_argument("--out_path", required=True)
args = parser.parse_args()

parts = ["body", "head", "left_leg", "right_leg", "left_arm", "right_arm"]
parts_masks = []
for part in parts:
    path = os.path.join(args.in_dir, part + ".png")
    assert os.path.exists(path)
    globals()[part] = cv2.imread(path, 0)
    parts_masks.append(globals()[part])
print("Found all parts.")

total_mask = np.zeros_like(body)
for part in parts_masks:
    total_mask += part
total_mask = total_mask.clip(total_mask, 255).astype(np.bool)

div = "-----------------"
print(div)

# First layer - total mask
final_img = np.zeros((body.shape[0], body.shape[1], 3)).astype(int)
final_img[:, :, 0] = total_mask * 255
print("First layer [:,:,0] is whole human mask")
print(div)

# Second layer - body
final_img[:, :, 1] = body.astype(np.bool) * 255
print("Second layer [:,:,1] is body")
print(div)

# Third layer - all body parts, not including body
print("Third layer [:,:,2] is body parts")
for i in range(1, len(parts)):
    fill_number = i * 50
    part = parts_masks[i].astype(np.bool)
    # FIXME: this way it is really sensitive to overlapping
    final_img[:, :, 2] += part * fill_number
    print("Part '{}' filled with {}".format(parts[i], fill_number))
print(div)

print("Finished.")
success = cv2.imwrite(args.out_path, final_img)
if success:
    print("Successfully written mask into", args.out_path)
else:
    print("Failed to write mask into", args.out_path)
