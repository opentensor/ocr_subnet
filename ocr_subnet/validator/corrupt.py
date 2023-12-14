# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import math
import random
from PIL import ImageFilter, ImageDraw
from ocr_subnet.utils.image import load


def corrupt_image(load_path: str, save_path: str, border: int=50, noise: float=0.1, spot: tuple[int]=(100,100), scale: float=0.95, theta: float=0.2, blur: float=0.5):
    """
    Applies transformations to pdf in order to make the document harder to parse

    Args:
        load_path (str): Path of original document
        save_path (str): Path to save corrupted document
        border (int, optional): Add border effect. Defaults to 50.
        noise (float, optional): Add noise effect. Defaults to 0.1.
        spot (tuple[int], optional): Add localized noise. Defaults to (100,100).
        scale (float, optional): Rescale image. Defaults to 0.95.
        theta (float, optional): Apply rotation. Defaults to 0.2.
        blur (float, optional): Add blur effect. Defaults to 0.5.
    """

    image = load(load_path, zoom_x=1.5, zoom_y=1.5)

    width, height = image.size

    # # imitate curled page by making the top-right and bottom-left corners go slightly up and darkening the edges
    if border is not None:
        for x in range(1,border):
            tone = 256 - int(250*(x/border-1)**2)
            for y in range(height):
                # only update color if the pixel is white
                if min(image.getpixel((x,y))) < 20:
                    continue
                image.putpixel((x, y), (tone, tone, tone))
                image.putpixel((width-x, y), (tone, tone, tone))

    # Apply noise
    if noise is not None:
        draw = ImageDraw.Draw(image)
        for _ in range(int(width * height * noise)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            delta = random.gauss(0,10)
            rgb = tuple([int(min(max(0,val+delta),256)) for val in image.getpixel((x,y))])
            draw.point((x, y), fill=rgb)

    if spot is not None:
        draw = ImageDraw.Draw(image)
        for _ in range(int(width * height * noise)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            delta = 10000 / (1 + math.sqrt((spot[0]-x)**2 + (spot[1]-y)**2))
            rgb = tuple([int(min(max(0,val-delta),256)) for val in image.getpixel((x,y))])
            draw.point((x, y), fill=rgb)

    # rescale the image within 10% to 20%
    if scale is not None:
        image = image.resize(size=(int(scale*width), int(scale*height)))

    # apply a rotation
    if theta is not None:
        image = image.rotate(theta, expand=True)

    # Apply blur
    if blur is not None:
        image = image.filter(ImageFilter.GaussianBlur(blur))

    # Save processed images back as a PDF
    image.save(save_path, "PDF", resolution=100.0, save_all=True)

