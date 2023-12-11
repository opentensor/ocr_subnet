import base64
from io import BytesIO
from PIL import Image


def serialize_image(image, format="JPEG"):
    """Converts PIL image to base64 string.
    """

    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def deserialize_image(base64_string):
    """Converts base64 string to PIL image.
    """

    return Image.open(BytesIO(base64.b64decode(base64_string)))