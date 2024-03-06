from datetime import timedelta, datetime

import starkbank
import uvicorn
from fastapi import FastAPI

from src.internal import get_client
from src.routers.v1 import sub_router
from src.utils.logging_config import logger

from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler()
app = FastAPI()


def job_create_invoice():
    time_now = datetime.now()

    invoices = [starkbank.Invoice(
        amount=40000,
        discounts=[{'percentage': 10, 'due': time_now + timedelta(days=3)}],
        due=time_now + timedelta(days=5),
        expiration=123456789,
        fine=2.5,
        interest=1.3,
        name="Arya Stark",
        tags=['War supply', 'Invoice #1234'],
        tax_id="012.345.678-90",
    )] * 8

    stark_bank = get_client()
    stark_bank.client.invoice.create(invoices)

    logger.info(f"Created eight invoices at {time_now}" )


def start_job():
    job = scheduler.add_job(job_create_invoice, 'interval', hours=3, id="invoice_create")

    scheduler.add_job(
        lambda: scheduler.remove_job(job.id),
        trigger='date',
        run_date=datetime.now() + timedelta(hours=24),
        id="remove_job"
    )

    scheduler.start()
    logger.info("Job Create invoice Started")


app.include_router(sub_router)
start_job()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
