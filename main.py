import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from filter import *
from segment import *
import time
from PIL import Image as im
import numpy as np
import os

def segment(in_image, sigma, k, min_size, output_file):
    start_time = time.time()
    height, width, band = in_image.shape
    print(f'Processing: {output_file}')
    print(f'Resolution:  {height} X {width}')
    smooth_red_band = smooth(in_image[:, :, 0], sigma)
    smooth_green_band = smooth(in_image[:, :, 1], sigma)
    smooth_blue_band = smooth(in_image[:, :, 2], sigma)

    # build graph
    edges_size = width * height * 4
    edges = np.zeros(shape=(edges_size, 3), dtype=object)
    num = 0
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int(y * width + (x + 1))
                edges[num, 2] = diff(smooth_red_band, smooth_green_band, smooth_blue_band, x, y, x + 1, y)
                num += 1
            if y < height - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + x)
                edges[num, 2] = diff(smooth_red_band, smooth_green_band, smooth_blue_band, x, y, x, y + 1)
                num += 1

            if (x < width - 1) and (y < height - 2):
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + (x + 1))
                edges[num, 2] = diff(smooth_red_band, smooth_green_band, smooth_blue_band, x, y, x + 1, y + 1)
                num += 1

            if (x < width - 1) and (y > 0):
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y - 1) * width + (x + 1))
                edges[num, 2] = diff(smooth_red_band, smooth_green_band, smooth_blue_band, x, y, x + 1, y - 1)
                num += 1
    # Segment
    u = segment_graph(width * height, num, edges, k)

    for i in range(num):
        a = u.find(edges[i, 0])
        b = u.find(edges[i, 1])
        if (a != b) and ((u.size(a) < min_size) or (u.size(b) < min_size)):
            u.join(a, b)

    num_cc = u.num_sets()
    output = np.zeros(shape=(height, width, 3))

    
    colors = np.zeros(shape=(height * width, 3))
    for i in range(height * width):
        colors[i, :] = random_rgb()

    for y in range(height):
        for x in range(width):
            comp = u.find(y * width + x)
            output[y, x, :] = colors[comp, :]

    elapsed_time = time.time() - start_time
    print(f'Exec. time = {int(elapsed_time / 60)} mins {int(elapsed_time % 60)} seconds')

    array = np.reshape(output, (height, width, -1))
    data = im.fromarray((array * 255).astype(np.uint8))
    data.save(output_file)


if __name__ == "__main__":
    sigma = 0.5
    k = 500
    min = 50

    cur_dir = os.getcwd()
    for entry in os.scandir(os.path.join(cur_dir,'input')):
        if (entry.path.endswith(".jpg") or 
            entry.path.endswith(".png") or 
            entry.path.endswith(".gif")) and entry.is_file():
            input_image=None
            with cbook.get_sample_data(entry.path) as image_file:
                input_image = plt.imread(image_file, format=None)
            
            if input_image is not None:
                segment(input_image, sigma, k, min, f'output/{entry.name}')
            else:
                print("error loading image")
