"""This is just a set of dummy tests"""

import logging


def test_success() -> None:
    """This is just a dummy test"""
    logging.info('This is just a dummy test that SUCCEEDS')
    assert True


def test_failure() -> None:
    """This is just a dummy test"""
    logging.info('This is just a dummy test that FAILS')
    raise AssertionError()
