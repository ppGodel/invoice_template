#!/usr/bin/env python3

from datetime import datetime
from dateutil.relativedelta import relativedelta
from pyinvoice.models import (
    InvoiceInfo,
    ServiceProviderInfo,
    ClientInfo,
    Item,
)
from pyinvoice.templates import SimpleInvoice
from typing import Dict, List
import json
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_pdf_mail(pass_data: Dict[str, str], receipents, pdf_path: str):
    msg = MIMEMultipart()
    message = "Hi, this is my monthly invoice"
    # setup the parameters of the message
    msg["From"] = pass_data["user"]
    msg["To"] = ", ".join(receipents)
    msg["Subject"] = "Invoice"
    # add in the message body
    msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(open(pdf_path).read()))
    # create server
    server = smtplib.SMTP("smtp.office365.com:587")
    server.starttls()
    # Login Credentials for sending the mail
    server.login(pass_data["user"], pass_data["pass"])

    # send the message via the server.
    server.sendmail(msg["From"], receipents, msg.as_string())
    server.quit()
    print("successfully sent email to %s:" % (msg["To"]))


def create_invoice(
    invoice_dir: Path,
    provider_info: Dict[str, str],
    client_info: Dict[str, str],
    items: List[Item] = [],
    invoice_number: int = 0,
    invoice_date: datetime = datetime.now(),
) -> str:
    invoice_date_str = invoice_date.strftime("%y%m")
    pdf_path = f"{str(invoice_dir)}/invoice{invoice_date_str}.pdf"
    doc = SimpleInvoice(pdf_path)
    doc.invoice_info = InvoiceInfo(invoice_number, invoice_date)
    doc.service_provider_info = ServiceProviderInfo(**provider_info)
    doc.client_info = ClientInfo(**client_info)
    for _item in items:
        doc.add_item(_item)
    doc.set_bottom_tip("Thank you for your business.")
    doc.finish()
    return pdf_path


def month_diff(start_date: datetime, end_date: datetime):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def create_spectrum_invoice(
    config_path: str = "./data.json",
    invoice_dir="./",
    invoice_date_str: str = datetime.now().strftime("%d-%m-%Y"),
):
    with open(config_path) as f:
        my_data = json.load(f)
    provider_info = my_data.get("provider")
    client_info = my_data.get("client")
    detail = my_data.get("detail")
    start_date = datetime.strptime(detail.get("start_date"), "%d-%m-%Y")
    month_salary = detail.get("month_salary")
    invoice_date = datetime.strptime(invoice_date_str, "%d-%m-%Y")
    billed_month = invoice_date - relativedelta(months=1)
    invoice_number = month_diff(start_date, invoice_date)
    items = [Item(billed_month.strftime("%B"), "", 1, month_salary)]
    return create_invoice(
        Path(invoice_dir),
        provider_info=provider_info,
        client_info=client_info,
        items=items,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
    )


if __name__ == "__main__":
    pass_data = {}
    with open("pass.json") as f:
        pass_data = json.load(f)
    pdf_path = create_spectrum_invoice()
    send_pdf_mail(pass_data=pass_data, receipents=["test@email.com"], pdf_path=pdf_path)
