import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from internal import PaymentTransfer

MOCK_TRANSFER = {
    "bank_code": "20018183",
    "branch": "0001",
    "account": "6341320293482496",
    "name": "Stark Bank S.A.",
    "tax_id": "20.018.183/0001-80",
    "account_type": "payment",
    "amount": 10000003,
}


@pytest.fixture
def mock_create_Transfer():
    mock_transfer = MagicMock()
    mock_transfer.client.Transfer = MagicMock()
    return mock_transfer


def test_creation_payment_transfer_successfuly(mock_create_Transfer):
    payment_transfer = PaymentTransfer(**MOCK_TRANSFER)
    payment_transfer.create(mock_create_Transfer)

    mock_create_Transfer.client.Transfer.assert_called_once()


def test_creation_payment_transfer_error(mock_create_Transfer):
    with pytest.raises(HTTPException) as excinfo:
        payment_transfer = PaymentTransfer(**MOCK_TRANSFER)
        payment_transfer.create(mock_create_Transfer)

    assert excinfo.value.status_code == 400



