import io
import fitz
import base64

from typing import List
from PIL import Image, ImageDraw


def serialize(image: Image, format: str="JPEG") -> str:
    """Converts PIL image to base64 string.
    """

    buffer = io.BytesIO()
    image.save(buffer, format=format)
    byte_string = buffer.getvalue()
    base64_string = base64.b64encode(byte_string).decode()
    return base64_string


def deserialize(base64_string: str) -> Image:
    """Converts base64 string to PIL image.
    """
    decoded_string = base64.b64decode(base64_string)
    buffer = io.BytesIO(decoded_string)
    return Image.open(buffer)


def load(pdf_path: str, page: int=0, zoom_x: float=1.0, zoom_y: float=1.0) -> Image:
    """Loads pdf image and converts to PIL image
    """

    # Read the pdf into memory
    pdf = fitz.open(pdf_path)
    page = pdf[page]

   # Set zoom factors for x and y axis (1.0 means 100%)
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    img_data = io.BytesIO(pix.tobytes('png'))

    # convert to PIL image
    return Image.open(img_data)

def draw_boxes(image: Image, response: List[dict], color='red'):
    """Draws boxes around text on the image
    """

    draw = ImageDraw.Draw(image)
    for item in response:
        draw.rectangle(item['position'], outline=color)

    return image