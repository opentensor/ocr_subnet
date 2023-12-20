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

import datetime
import random

from typing import List

from faker import Faker

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

from ocr_subnet.validator.corrupt import corrupt_image
from ocr_subnet.utils.image import load, serialize

seed = 0
fake = Faker()
# Seed the Faker instance
fake.seed_instance(seed)

# set random seed
random.seed(seed)

def apply_invoice_template(invoice_data: dict, path: str) -> List[dict]:
    """
    Generates an invoice from raw data and saves as pdf

    Args:
    - invoice_data (dict): contents of invoice
    - path (str): path to save pdf file

    Returns:
    - List[dict]: contents of invoice with text, position and font information for each section
    """

    c = canvas.Canvas(path, pagesize=letter)
    w, h = c._pagesize
    c.setLineWidth(.3)

    font_name = random.choice(['Helvetica','Times-Roman'])
    font_size = random.choice([10, 11, 12])
    c.setFont(font_name, font_size)

    data = []
    def write_text(x, y, text):
        c.drawString(x, y, text)
        # scale x and y by the page size and estimate bounding box based on font size
        # position = [x0, y0, x1, y1]
        text_width = pdfmetrics.stringWidth(text, font_name, font_size)
        position = [
            x/w,
            1 - (y - 0.2*font_size)/h,
            (x + text_width)/w,
            1 - (y + 0.8*font_size)/h
        ]

        data.append({'position': position, 'text': text, 'font': {'family': font_name, 'size': font_size}})

    # Draw the invoice header
    write_text(30, 750, invoice_data['company_name'])

    write_text(400, 750, "Invoice Date: " + invoice_data['invoice_date'])
    write_text(400, 735, "Invoice #: " + invoice_data['invoice_number'])

    write_text(30, 735, invoice_data['company_address'])
    write_text(30, 720, invoice_data['company_city_zip'])

    # Draw the bill to section
    write_text(30, 690, "Bill To:")
    write_text(120, 690, invoice_data['customer_name'])

    # Table headers
    write_text(30, 650, "Description")
    write_text(300, 650, "Qty")
    write_text(460, 650, "Cost")
    c.line(30, 645, 560, 645)

    # List items
    line_height = 625
    total = 0
    for item in invoice_data['items']:
        write_text(30, line_height, item['desc'])
        write_text(300, line_height, str(item['qty']))
        write_text(460, line_height, "${:.2f}".format(item['cost']))
        total += item['qty'] * item['cost']
        line_height -= 15

    # Draw the total cost
    write_text(400, line_height - 15, f"Total: ${total:,.2f}" )

    # Terms and Conditions
    write_text(30, line_height - 45, "Terms:")
    write_text(120, line_height - 45, invoice_data['terms'])

    c.save()
    return data


def invoice(path: str, n_items: int=None, corrupt: bool=True) -> dict:
    """Create a synthetic invoice and save as pdf

    Args:
        path (str): Path to save invoice document.
        n_items (int): Number of items in document. Defaults to None.
        corrupt (bool): Make the document harder to parse by adding noise etc.

    Returns:
        _type_: _description_
    """

    items_list = [
        {"desc": "Web hosting", "cost": 100.00},
        {"desc": "Domain registration", "cost": 10.00},
        {"desc": "SSL certificate", "cost": 5.50},
        {"desc": "Web design", "cost": 500.00},
        {"desc": "Web development", "cost": 500.00},
        {"desc": "SEO", "cost": 100.00},
        {"desc": "Content creation", "cost": 300.00},
        {"desc": "Social media marketing", "cost": 400.00},
        {"desc": "Email marketing", "cost": 150.00},
        {"desc": "PPC advertising", "cost": 200.00},
        {"desc": "Analytics", "cost": 400.00},
        {"desc": "Consulting", "cost": 700.00},
        {"desc": "Training", "cost": 1200.00},
        {"desc": "Maintenance", "cost": 650.00},
        {"desc": "Support", "cost": 80.00},
        {"desc": "Graphic design", "cost": 310.00},
        {"desc": "Logo design", "cost": 140.00},
        {"desc": "Branding", "cost": 750.00},
    ]
    if n_items is None:
        n_items = random.randint(8, len(items_list))

    def random_items(n):
        items = sorted(random.sample(items_list, k=n), key=lambda x: x['desc'])
        return [{**item, 'qty':random.randint(1,5)} for item in items]

    # Sample data for the invoice
    invoice_info = {
        "company_name": fake.company(),
        "company_address": fake.address(),
        "company_city_zip": f'{fake.city()}, {fake.zipcode()}',
        "company_phone": fake.phone_number(),
        "customer_name": fake.name(),
        "invoice_date": datetime.date.fromtimestamp(1700176424-random.random()*5e8).strftime("%B %d, %Y"),
        "invoice_number": f"INV{random.randint(1,10000):06}",
        "items": random_items(n_items),
        "terms": f"Payment due within {random.choice([7, 14, 30, 60, 90])} days"
    }

    # Use the function and pass the data and the filename you want to save as
    data = apply_invoice_template(invoice_info, path)

    # overwrite image file with corrupted version
    if corrupt:
        corrupt_image(path, path)

    image = load(path)
    base64_image = serialize(image)

    return {'image':image, 'labels':data, 'path':path, 'base64_image': base64_image}
