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


def create_invoice(
    provider_info: Dict[str, str],
    client_info: Dict[str, str],
    items: List[Item] = [],
    invoice_number: int = 0,
    invoice_date: datetime = datetime.now(),
):
    invoice_date_str = invoice_date.strftime("%y%m")
    # month_str = invoice_date.strftime("%B")
    doc = SimpleInvoice(f"invoice{invoice_date_str}.pdf")
    doc.invoice_info = InvoiceInfo(invoice_number, invoice_date)
    doc.service_provider_info = ServiceProviderInfo(**provider_info)
    doc.client_info = ClientInfo(**client_info)
    # doc.add_item(Item(month_str, "", 1, ""))
    for _item in items:
        doc.add_item(_item)
    doc.set_bottom_tip("Thank you for your business.")
    doc.finish()


def month_diff(start_date: datetime, end_date: datetime):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def create_spectrum_invoice(
    config_path: str = "./data.json",
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
    create_invoice(
        provider_info=provider_info,
        client_info=client_info,
        items=items,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
    )


if __name__ == "__main__":
    create_spectrum_invoice()
