from json import dumps
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
# from main import app  # Import your FastAPI instance
import pytest
from starlette import status

from internal import get_client
from main import app

WEBHOOK_INVOICE_DATA = {
        "event": {
            "is_delivered": False,
            "created": "2024-03-02T21:14:56.528329+00:00",
            "id": "5234984252080128",
            "log": {
                "created": "2024-03-02T21:14:56.262632+00:00",
                "errors": [],
                "id": "6494089193193472",
                "invoice": {
                    "amount": 300,
                    "brcode": "00020101021226890014br.gov.bcb.pix2567brcode-h.sandbox.starkinfra.com/v2/4d258ed4a2c146a789056aef3e97a3735204000053039865802BR5925Stark Bank S.A. - Institu6009Sao Paulo62070503***6304B7F2",
                    "created": "2024-03-02T21:14:56.136377+00:00",
                    "descriptions": [
                        {
                            "key": "Arya",
                            "value": "Not today"
                        }
                    ],
                    "discountAmount": 0,
                    "discounts": [],
                    "due": "2024-03-04T21:14:56.127503+00:00",
                    "expiration": 5097600,
                    "fee": 0,
                    "fine": 2,
                    "fineAmount": 0,
                    "id": "5368189286350848",
                    "interest": 1,
                    "interestAmount": 0,
                    "link": "https://test4339673.sandbox.starkbank.com/invoicelink/4d258ed4a2c146a789056aef3e97a373",
                    "name": "Arya Stark",
                    "nominalAmount": 300,
                    "pdf": "https://sandbox.api.starkbank.com/v2/invoice/4d258ed4a2c146a789056aef3e97a373.pdf",
                    "rules": [],
                    "splits": [],
                    "status": "created",
                    "tags": [],
                    "taxId": "012.345.678-90",
                    "transactionIds": [],
                    "updated": "2024-03-02T21:14:56.262682+00:00"
                },
                "type": "created"
            },
            "subscription": "invoice",
            "workspaceId": "4884145050222592"
        }
    }


@pytest.fixture
def mock_return_value_webhook_invoice(mocker):
    mock = mocker.MagicMock()
    mock.status.return_value = "created"
    return mock


@pytest.fixture
def stark_bank_singleton_mock(mocker, mock_return_value_webhook_invoice):
    # Mock the StarkBankSingleton instance and its methods
    mock = mocker.MagicMock()
    mock.client.transfer.create.return_value = [mock_return_value_webhook_invoice]
    return mock


@pytest.fixture
def client():
    # Create a test client for your FastAPI app
    client = TestClient(app)
    client.headers["Content-Type"] = "application/json"
    return client


def test_invoice_webhook_success(client, stark_bank_singleton_mock, mocker):
    app.dependency_overrides[get_client] = lambda: stark_bank_singleton_mock

    # Mock to class PaymentTransfer
    mock_payment_transfer = mocker.patch(
        'src.routers.v1.webhook.PaymentTransfer',
        return_value=mocker.MagicMock()
    )
    mock_payment_transfer.create = mocker.MagicMock()

    # Act
    response = client.post("/v1/webhook/invoice", json=WEBHOOK_INVOICE_DATA)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Invoice Received!"
    stark_bank_singleton_mock.client.transfer.create.assert_called_once()
