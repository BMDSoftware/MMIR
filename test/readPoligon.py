import json
from matplotlib.patches import Polygon
import numpy as np


f = open('test_files/json_coco_017_1.json')
data = json.load(f)

ann = data["annotations"]

polygons = []
counter = 0

for an in ann:
    counter =  counter +1

    seg = an["segmentation"]
    for s in seg:

        poly = np.array(s).reshape((int(len(s) / 2), 2))
        polygons.append(poly)

print(polygons[0])
print(counter)

