from abc import ABC, abstractmethod
from datetime import datetime, timezone

from fastapi import HTTPException
from loguru import logger

from starkbank.transfer import Rule


class Payment(ABC):
    @abstractmethod
    def check_amount(self, amount: int):
        pass

    @abstractmethod
    def create(self):
        pass


def transform_to_datetime(time):
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")


class PaymentTransfer(Payment):
    now: datetime = datetime.now(timezone.utc)

    def __init__(
            self,
            id: str,
            bank_code: str,
            branch: str,
            account: str,
            name: str,
            tax_id: str,
            account_type: str,
            amount: int,
            due: datetime,
            created: datetime,
            fine: int,
            interest: int,
            expiration: int,
    ):
        self.id = id
        self._bank_code = bank_code
        self._branch = branch
        self._account = account
        self._name = name
        self._tax_id = tax_id
        self._account_type = account_type
        self._amount = self.check_amount(amount)
        self.fee = None
        self.discounts = None
        self.due = due.replace(tzinfo=timezone.utc)
        self.created = created.replace(tzinfo=timezone.utc)
        self.fine = fine
        self.interest = interest
        self.expiration = expiration

    def check_amount(self, amount: int) -> int:
        if amount > 1000001:  # 100 reais
            logger.warning(f"Amount passed the maximum transfer value {amount} to user {self._name}")
            raise HTTPException(status_code=400, detail="Amount can not pass 100 reais")
        else:
            return amount

    def check_due_date(self):
        return self.now > self.due

    def is_invoice_expired(self):
        return (
                datetime.fromtimestamp(
                    self.expiration,
                    timezone.utc
                ) < self.now
        )

    def calculate_delay_fine(self):
        fee = self.fine / 100
        amount_fee = fee * self._amount

        self._amount = amount_fee

    def calculate_delay_interest(self):
        if self.now > self.due:
            time_difference = self.now - self.due
        else:
            time_difference = self.due - self.now

        fee = self.interest / 100

        for multi_months in range(29, time_difference.days, 30):
            self._amount = (fee + 1) * self._amount

    def should_calculate_fees(self):
        if self.check_due_date() and not self.is_invoice_expired():
            logger.info(f"Calculating fee amount to invoice {self.id}")
            self.calculate_delay_fine()
            self.calculate_delay_interest()
        else:
            logger.info(f"No fee calculation amount was necessary to invoice {self.id}")

    def create(self, sb_client):
        transfer_object = sb_client.client.Transfer(
            amount=self._amount,
            bank_code=self._bank_code,
            branch_code=self._branch,
            account_number=self._account,
            account_type=self._account_type,
            name=self._name,
            tax_id=self._tax_id,
            rules=[
                Rule(
                    key="resendingLimit",
                    value=2
                )
            ]
        )
        logger.info(f"Transfer object {transfer_object}")

        self.should_calculate_fees()

        return transfer_object
