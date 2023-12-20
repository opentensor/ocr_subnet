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

from typing import List

def group_and_merge_boxes(data: List[dict], xtol: int=25, ytol: int=5) -> List[dict]:
    """
    Combines boxes that are close together into a single box so that the text is grouped into sections.

    Args:
    - data (list): List of dictionaries containing the position, font and text of each section
    - xtol (int): Maximum distance between boxes in the x direction to be considered part of the same section
    - ytol (int): Maximum distance between boxes in the y direction to be considered part of the same section

    Returns:
    - list: List of dictionaries containing the position, font and text of each section
    """
    # Ensure all data items are valid and have a 'position' key
    data = [box for box in data if box is not None and 'position' in box]

    # Step 1: Group boxes by lines
    lines = []
    for box in data:
        added_to_line = False
        for line in lines:
            if line and abs(line[0]['position'][1] - box['position'][1]) <= ytol:
                line.append(box)
                added_to_line = True
                break
        if not added_to_line:
            lines.append([box])

    # Step 2: Sort and merge within each line
    merged_data = []
    for line in lines:
        line.sort(key=lambda item: item['position'][0])  # Sort by x1
        i = 0
        while i < len(line) - 1:
            box1 = line[i]['position']
            box2 = line[i + 1]['position']
            if abs(box1[2] - box2[0]) <= xtol:  # Check horizontal proximity
                new_box = {'position': [min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[2], box2[2]), max(box1[3], box2[3])],
                        'text': line[i]['text'] + ' ' + line[i + 1]['text']}
                line[i] = new_box
                del line[i + 1]
            else:
                i += 1
        merged_data.extend(line)

    return merged_data