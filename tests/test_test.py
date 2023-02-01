"""This is just a set of dummy tests"""

import logging

from click.testing import CliRunner

from yojenkins.__main__ import auth
from yojenkins.cli_sub_commands.auth import show


def test_success() -> None:
    """This is just a dummy test"""
    logging.info("This is just a dummy test that SUCCEEDS")
    assert True


# def test_failure() -> None:
#     """This is just a dummy test"""
#     logging.info("This is just a dummy test that FAILS")
#     assert False

def test_auth_show():
    runner = CliRunner()
    result = runner.invoke(show, [])
    logging.fatal("TEST")
    logging.fatal(result.exit_code)
    logging.fatal(result.output)

    assert result.exit_code == 0

    
