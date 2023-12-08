import os
import datetime
import random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



def apply_invoice_template(invoice_data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    w, h = c._pagesize
    print(w,h)
    c.setLineWidth(.3)
    font = {'family': 'Helvetica', 'size': 12}
    units = font.get('size')
    c.setFont(font.get('family'), units)

    data = []
    def write_text(x, y, text):
        c.drawString(x, y, text)
        # scale x and y by the page size and estimate bounding box based on font size
        # position = [x0, y0, x1, y1]
        position = [
            x/w,
            1 - (y - 0.2*units)/h,
            (x + (2 + len(text)) * 0.5*units)/w,
            1 - (y + 1.2*units)/h
        ]

        data.append({'position': position, 'text': text, 'font': font})

    # Draw the invoice header
    write_text(30, 750, invoice_data['company_name'])
    write_text(30, 735, invoice_data['company_address'])
    write_text(30, 720, invoice_data['company_city_zip'])
    write_text(400, 750, "Invoice Date: " + invoice_data['invoice_date'])
    write_text(400, 735, "Invoice #: " + invoice_data['invoice_number'])

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


def create_invoice(root_dir):

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

    def random_items(n):
        items = sorted(random.sample(items_list, k=n), key=lambda x: x['desc'])
        return [{**item, 'qty':random.randint(1,5)} for item in items]

    fake = Faker()

    # Sample data for the invoice
    invoice_info = {
        "company_name": fake.company(),
        "company_address": fake.address(),
        "company_city_zip": f'{fake.city()}, {fake.zipcode()}',
        "company_phone": fake.phone_number(),
        "customer_name": fake.name(),
        "invoice_date": datetime.date.fromtimestamp(1700176424-random.random()*5e8).strftime("%B %d, %Y"),
        "invoice_number": f"INV{random.randint(1,10000):06}",
        "items": random_items(random.randint(3,15)),
        "terms": "Payment due within 30 days"
    }

    # make a random hash for the filename
    filename = f"{fake.sha256()}.pdf"
    path = os.path.join(root_dir, filename)
    
    # Use the function and pass the data and the filename you want to save as
    data = apply_invoice_template(invoice_info, path)

    return data, path