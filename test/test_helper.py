import pytest
from helper import Helper


def test_init_points():
    h = Helper().init_points(
        ((8, 8), 0),
        ((0, 0), 5),
    ).reset().assert_pos_player(
        ((8, 8), 0),
        ((0, 0), 5),
        ((0, 1), 1),
    )


def test_assert_no_error_log_warning():
    h = Helper()
    from loguru import logger
    logger.warning('msg')
    h.assert_no_error_log()


def test_assert_no_error_log_error():
    h = Helper()
    from loguru import logger
    logger.error('msg')
    with pytest.raises(AssertionError):
        h.assert_no_error_log()


def test_assert_no_error_log_critical():
    h = Helper()
    from loguru import logger
    logger.critical('msg')
    with pytest.raises(AssertionError):
        h.assert_no_error_log()
