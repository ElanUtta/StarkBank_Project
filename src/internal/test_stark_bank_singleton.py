import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from fastapi import HTTPException

# Assume PaymentTransfer is in payment_transfer.py, adjust the import accordingly
from src.internal.PaymentTransfer import PaymentTransfer, transform_to_datetime

# Constants for the tests
BANK_CODE = "000"
BRANCH = "0001"
ACCOUNT = "123456"
NAME = "Test Name"
TAX_ID = "123.456.789-00"
ACCOUNT_TYPE = "checking"
AMOUNT = 100
DUE_DATE = datetime.now(timezone.utc) + timedelta(days=5)
CREATED_DATE = datetime.now(timezone.utc) - timedelta(days=1)
FINE = 2
INTEREST = 1
EXPIRATION = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())


# Mock sb_client for all tests in this module
@pytest.fixture(scope="module")
def sb_client():
    client_mock = MagicMock()
    # Configure the mock object here as needed
    yield client_mock


# Keep the time-related fixtures dynamically computed to avoid expired test scenarios
@pytest.fixture
def due_date():
    return datetime.now(timezone.utc) + timedelta(days=3)


@pytest.fixture
def created_date():
    return datetime.now(timezone.utc) - timedelta(days=2)


@pytest.fixture
def expiration_timestamp(due_date):
    return int((due_date + timedelta(days=30)).timestamp())


@pytest.fixture
def payment_transfer(due_date, created_date, expiration_timestamp):
    return PaymentTransfer(
        id="123",
        bank_code=BANK_CODE,
        branch=BRANCH,
        account=ACCOUNT,
        name=NAME,
        tax_id=TAX_ID,
        account_type=ACCOUNT_TYPE,
        amount=AMOUNT,
        due=due_date,
        created=created_date,
        fine=FINE,
        interest=INTEREST,
        expiration=expiration_timestamp,
    )


def test_create_payment_transfer():
    payment_transfer = PaymentTransfer(
        id="123",
        bank_code=BANK_CODE,
        branch=BRANCH,
        account=ACCOUNT,
        name=NAME,
        tax_id=TAX_ID,
        account_type=ACCOUNT_TYPE,
        amount=AMOUNT,
        due=DUE_DATE,
        created=CREATED_DATE,
        fine=FINE,
        interest=INTEREST,
        expiration=EXPIRATION,
    )
    assert payment_transfer._amount == AMOUNT


def test_check_amount_valid(sb_client):
    payment_transfer = PaymentTransfer(
        id="123",
        bank_code=BANK_CODE,
        branch=BRANCH,
        account=ACCOUNT,
        name=NAME,
        tax_id=TAX_ID,
        account_type=ACCOUNT_TYPE,
        amount=AMOUNT,
        due=DUE_DATE,
        created=CREATED_DATE,
        fine=FINE,
        interest=INTEREST,
        expiration=EXPIRATION,
    )
    # Ensure method check_amount returns the correct amount when within limits
    assert payment_transfer.check_amount(100) == 100


def test_check_amount_invalid(sb_client):
    with pytest.raises(HTTPException) as exc_info:
        payment_transfer = PaymentTransfer(
            id="123",
            bank_code=BANK_CODE,
            branch=BRANCH,
            account=ACCOUNT,
            name=NAME,
            tax_id=TAX_ID,
            account_type=ACCOUNT_TYPE,
            amount=1000002,  # Invalid amount beyond threshold
            due=DUE_DATE,
            created=CREATED_DATE,
            fine=FINE,
            interest=INTEREST,
            expiration=EXPIRATION,
        )
        payment_transfer.check_amount(1000002)
    assert exc_info.value.status_code == 400
    assert "Amount can not pass 100 reais" in exc_info.value.detail


def test_payment_transfer_create_transfer(sb_client):
    payment_transfer = PaymentTransfer(
        id="123",
        bank_code=BANK_CODE,
        branch=BRANCH,
        account=ACCOUNT,
        name=NAME,
        tax_id=TAX_ID,
        account_type=ACCOUNT_TYPE,
        amount=AMOUNT,
        due=DUE_DATE,
        created=CREATED_DATE,
        fine=FINE,
        interest=INTEREST,
        expiration=EXPIRATION,
    )
    # Mock the creation of the transfer object to test the create method
    sb_client.client.Transfer = MagicMock(return_value="mock_transfer_object")
    transfer = payment_transfer.create(sb_client)
    assert sb_client.client.Transfer.called
    assert transfer == "mock_transfer_object"


def test_transform_to_datetime():
    time_str = "2024-03-02T21:14:56.528329+00:00"
    expected_datetime = datetime(2024, 3, 2, 21, 14, 56, 528329, tzinfo=timezone.utc)
    actual_datetime = transform_to_datetime(time_str)
    assert actual_datetime == expected_datetime


def test_due_date_before_now(payment_transfer):
    # Make due date in the past to test overdue scenario
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    assert payment_transfer.check_due_date()


def test_due_date_after_now(payment_transfer):
    # Due date in the future should not be considered overdue
    assert not payment_transfer.check_due_date()


def test_expiration_date_before_now(payment_transfer):
    # Set the expiration date in the past
    payment_transfer.expiration = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())
    assert payment_transfer.is_invoice_expired()


def test_expiration_date_after_now(payment_transfer):
    # Expiration date in the future should not be expired
    assert payment_transfer.is_invoice_expired() is False


def test_calculate_delay_fine(payment_transfer):
    # Overdue payment should have fine calculated
    initial_amount = payment_transfer._amount
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    payment_transfer.calculate_delay_fine()
    expected_fine = initial_amount * (FINE / 100)
    assert payment_transfer._amount == expected_fine


def test_calculate_delay_interest(payment_transfer):
    # Overdue payment should accrue interest
    initial_amount = payment_transfer._amount
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=60, minutes=10)  # Overdue by 2 months
    payment_transfer.calculate_delay_interest()

    expected_interest = initial_amount * (1 + INTEREST / 100) ** 2  # Compounded monthly
    assert int(payment_transfer._amount) == int(expected_interest)  # Interest is 1% monthly compounded


def test_should_not_calculate_fees_if_not_due(payment_transfer):
    # Payment is not overdue, fees should not be applied
    initial_amount = payment_transfer._amount
    payment_transfer.should_calculate_fees()
    assert payment_transfer._amount == initial_amount  # Amount should remain the same


def test_should_calculate_fees_if_due_and_not_expired(payment_transfer):
    # Payment overdue but not expired should have fees
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    payment_transfer.should_calculate_fees()
    # Fine and interest should be applied
    assert payment_transfer._amount != AMOUNT
