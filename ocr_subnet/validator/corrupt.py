import pdf2image
import math
import random
from IPython.display import display
from PIL import ImageFilter, ImageDraw



def corrupt_image(input_pdf_path, output_pdf_path, theta=1, border=50, noise=0.1, scale=0.95, blur=1, spot=(100,100)):
    # Convert PDF to images
    images = pdf2image.convert_from_path(input_pdf_path)

    processed_images = []

    for i, image in enumerate(images):

        display(image)
        width, height = image.size


        # # imitate curled page by making the top-right and bottom-left corners go slightly up and darkening the edges
        if border is not None:
            for x in range(1,border):
                tone = 256 - int(250*(x/border-1)**2)
                for y in range(height):
                    # only update color if the pixel is white
                    if min(image.getpixel((x,y))) < 20:
                        print(image.getpixel((x,y)))
                        continue
                    image.putpixel((x, y), (tone, tone, tone))
                    image.putpixel((width-x, y), (tone, tone, tone))

        # Apply noise
        if noise is not None:
            draw = ImageDraw.Draw(image)
            for _ in range(int(width * height * noise)):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                # TODO: Parameterize
                delta = random.gauss(0,50)
                rgb = tuple([int(min(max(0,val+delta),256)) for val in image.getpixel((x,y))])
                draw.point((x, y), fill=rgb)

        if spot is not None:
            draw = ImageDraw.Draw(image)
            for _ in range(int(width * height * noise)):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                #TODO: Parameterize
                delta = 100000 / (1 + math.sqrt((spot[0]-x)**2 + (spot[1]-y)**2))
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

        display(image)

        processed_images.append(image)

    # Save processed images back as a PDF
    processed_images[0].save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=processed_images[1:])
