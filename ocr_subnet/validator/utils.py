import editdistance


def get_iou(bb1, bb2 = None):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    NOTE: Thanks to this guy! https://stackoverflow.com/questions/25349178/calculating-percentage-of-bounding-box-overlap-for-image-detector-evaluation

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float: Normalized between 0 and 1.
    """

    if not bb2:
        return 1.0

    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou


def get_edit_distance(text1: str, text2: str = None):
    """Calculate the edit distance between two strings.

    Parameters
    ----------
    text1 : str
        The first string.
    text2 : str
        The second string.

    Returns
    -------
    float
        The edit distance between the two strings, normalized to be between 0 and 1.
    """
    if not text2:
        return 1.0

    return editdistance.eval(text1, text2) / max(len(text1), len(text2))

def get_font_distance(font1: dict, font2: dict = None):
    """Calculate the distance between two fonts.

    Parameters
    ----------
    font1 : dict
        The first font.
    font2 : dict
        The second font.

    Returns
    -------
    float
        The distance between the two fonts. Normalized to be between 0 and 1.
    """
    if not font2:
        return 1.0

    font_size_loss = abs(font1['size'] - font2['size']) / max(font1['size'], font2['size'])
    font_family_loss = 0.0 if font1['family'] == font2['family'] else 1.0
    return (font_size_loss + font_family_loss) / 2