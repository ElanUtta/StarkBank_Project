import pytest
from datetime import datetime, timedelta, timezone

from src.internal.payment_transfer import PaymentTransfer, transform_to_datetime

# Test constants
BANK_CODE = "000"
BRANCH = "0001"
ACCOUNT = "123456"
NAME = "Test Name"
TAX_ID = "123.456.789-00"
ACCOUNT_TYPE = "checking"
AMOUNT = 100
FINE = 2  # 2%
INTEREST = 1  # 1% every 30 days



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


def test_transform_to_datetime():
    time_str = "2024-03-02T21:14:56.528329+00:00"
    expected_datetime = datetime(2024, 3, 2, 21, 14, 56, 528329, tzinfo=timezone.utc)
    actual_datetime = transform_to_datetime(time_str)
    assert actual_datetime == expected_datetime


def test_due_date_before_now(payment_transfer):
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    assert payment_transfer.check_due_date()


def test_due_date_after_now(payment_transfer):
    assert not payment_transfer.check_due_date()


def test_expiration_date_before_now(payment_transfer):
    payment_transfer.expiration = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())
    assert payment_transfer.is_invoice_expired()


def test_expiration_date_after_now(payment_transfer):
    assert payment_transfer.is_invoice_expired() is False


def test_calculate_delay_fine(payment_transfer):
    initial_amount = payment_transfer._amount
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    payment_transfer.calculate_delay_fine()
    expected_fine = initial_amount * (FINE / 100)
    assert payment_transfer._amount == expected_fine


def test_calculate_delay_interest(payment_transfer):
    initial_amount = payment_transfer._amount
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=61)  # Overdue by 2 months
    payment_transfer.calculate_delay_interest()
    expected_interest = initial_amount * (1 + INTEREST / 100) ** 2  # Compounded monthly
    assert int(payment_transfer._amount) == int(expected_interest)  # Interest is 1% monthly compounded


def test_should_not_calculate_fees_if_not_due(payment_transfer):
    initial_amount = payment_transfer._amount
    payment_transfer.should_calculate_fees()
    assert payment_transfer._amount == initial_amount  # Amount should remain the same


def test_should_calculate_fees_if_due_and_not_expired(payment_transfer):
    payment_transfer.due = datetime.now(timezone.utc) - timedelta(days=1)
    payment_transfer.should_calculate_fees()
    assert payment_transfer._amount != AMOUNT
