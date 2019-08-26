import pytest

from src.shipchain_common.exceptions import RPCError


@pytest.fixture
def hw_string():  # This is only defined as a fixture as an example of fixtures in pytest
    return "Hello, world!"


def test_rpc_error(hw_string):
    with pytest.raises(RPCError, match=hw_string):
        raise RPCError(hw_string)
