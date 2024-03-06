import pytest
from unittest.mock import patch, MagicMock
from src.internal.stark_bank_singleton import StarkBankSingleton, get_client
from src.utils import Credentials

ENVIRONMENT = 'sandbox'
PROJECT_ID = '9999999999999999'


def reset_starkbank_singleton():
    StarkBankSingleton._instance = None


@patch('src.internal.stark_bank_singleton.ENVIRONMENT', ENVIRONMENT)
@patch('src.internal.stark_bank_singleton.PROJECT_ID', PROJECT_ID)
@patch('src.internal.stark_bank_singleton.starkbank.Project')
def test_singleton_behavior(ProjectMock):
    # Define the behavior of the mock Credentials
    credentials_mock = MagicMock(spec=Credentials)
    credentials_mock.get.return_value = 'fake_private_key'

    # Ensure the singleton resets for each test
    StarkBankSingleton._instance = None

    # First instance creation
    client1 = StarkBankSingleton(credentials_mock)

    # Second instance "creation" should retrieve the same instance
    client2 = StarkBankSingleton(credentials_mock)

    assert client1 is client2
    ProjectMock.assert_called_once_with(
        environment=ENVIRONMENT,  # Use the patched value directly
        id=PROJECT_ID,  # Use the patched value directly
        private_key='fake_private_key'  # Use the return value from the credentials mock
    )


@patch('src.internal.stark_bank_singleton.ENVIRONMENT', ENVIRONMENT)
@patch('src.internal.stark_bank_singleton.PROJECT_ID', PROJECT_ID)
@patch('src.internal.stark_bank_singleton.starkbank.Project')
def test_initialize_project(ProjectMock):
    reset_starkbank_singleton()

    credentials_mock = MagicMock(spec=Credentials)
    credentials_mock.get.return_value = 'fake_private_key'

    stark_bank_singleton = StarkBankSingleton(credentials_mock)
    assert stark_bank_singleton.client is not None
    ProjectMock.assert_called_with(
        environment=ENVIRONMENT,
        id=PROJECT_ID,
        private_key=credentials_mock.get.return_value
    )


@patch('src.internal.stark_bank_singleton.ENVIRONMENT', ENVIRONMENT)
@patch('src.internal.stark_bank_singleton.PROJECT_ID', PROJECT_ID)
@patch('src.internal.stark_bank_singleton.starkbank.Project')
def test_get_client(ProjectMock):
    reset_starkbank_singleton()

    credentials_mock = MagicMock(spec=Credentials)
    credentials_mock.get.return_value = 'fake_private_key'

    with patch('src.internal.stark_bank_singleton.CredentialsEnv', return_value=credentials_mock):
        client = get_client()

    assert isinstance(client, StarkBankSingleton)
    ProjectMock.assert_called_with(
        environment=ENVIRONMENT,
        id=PROJECT_ID,
        private_key=credentials_mock.get.return_value
    )
