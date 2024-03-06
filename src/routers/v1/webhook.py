from fastapi import Request, APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from src.schema.invoice import WebhookPayload
from src.utils.logging_config import logger
from src.internal.payment_transfer import PaymentTransfer
from src.internal.stark_bank_singleton import StarkBankSingleton, get_client

webhook_router = APIRouter(
    prefix="/webhook",
    tags=["hebwook"],
    responses={
        404: {"description": "Not Found"}
    }
)


@webhook_router.post("/invoice")
async def invoice_webhook(payload: WebhookPayload, sb_client: StarkBankSingleton = Depends(get_client)):
    id = payload.event.log.invoice.id
    amount = payload.event.log.invoice.amount
    fee = payload.event.log.invoice.fee
    due = payload.event.log.invoice.due
    created = payload.event.log.invoice.created
    fine = payload.event.log.invoice.fine
    interest = payload.event.log.invoice.interest
    expiration = payload.event.log.invoice.expiration

    if not amount:
        raise HTTPException(status_code=400, detail="Missing amount value")

    payment_transfer = PaymentTransfer(
        id=id,
        bank_code="20018183",
        branch="0001",
        account="6341320293482496",
        name="Stark Bank S.A.",
        tax_id="20.018.183/0001-80",
        account_type="payment",
        amount=amount - fee,
        due=due,
        created=created,
        fine=fine,
        interest=interest,
        expiration=expiration,
    )

    payment_transfer = payment_transfer.create(sb_client)

    result = sb_client.client.transfer.create([
        payment_transfer
    ])

    print(result, 'olololol')

    logger.info(
        f"Payment transfered to {payment_transfer.name}, with "
        f"account_type: {payment_transfer.account_type},"
        f"with status: {result[0].status}"
    )

    return JSONResponse(status_code=200, content="Invoice Received!")
