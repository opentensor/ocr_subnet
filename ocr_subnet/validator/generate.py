import os
import datetime
import random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def apply_invoice_template(invoice_data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setLineWidth(.3)
    c.setFont('Helvetica', 12)

    # Draw the invoice header
    c.drawString(30, 750, invoice_data['company_name'])
    c.drawString(30, 735, invoice_data['company_address'])
    c.drawString(30, 720, invoice_data['company_city_zip'])
    c.drawString(400, 750, "Invoice Date: " + invoice_data['invoice_date'])
    c.drawString(400, 735, "Invoice #: " + invoice_data['invoice_number'])

    # Draw the bill to section
    c.drawString(30, 690, "Bill To:")
    c.drawString(120, 690, invoice_data['customer_name'])

    # Table headers
    c.drawString(30, 650, "Description")
    c.drawString(300, 650, "Qty")
    c.drawString(460, 650, "Cost")
    c.line(30, 645, 560, 645)

    # List items
    line_height = 625
    total = 0
    for item in invoice_data['items']:
        c.drawString(30, line_height, item['desc'])
        c.drawString(300, line_height, str(item['qty']))
        c.drawString(460, line_height, "${:.2f}".format(item['cost']))
        total += item['qty'] * item['cost']
        line_height -= 15

    # Draw the total cost
    c.drawString(400, line_height - 15, f"Total: ${total:,.2f}" )

    # Terms and Conditions
    c.drawString(30, line_height - 45, "Terms:")
    c.drawString(120, line_height - 45, invoice_data['terms'])

    c.save()

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
    apply_invoice_template(invoice_info, path)

    return path