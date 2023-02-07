import pytest
from helper import Helper


class TestInitPoints:

    def test(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            5: (0, 0),
        })
        h.reset()
        assert h.gamecore.players[0].pos == (8, 8)
        assert h.gamecore.players[5].pos == (0, 0)
        assert h.gamecore.players[1].pos == (0, 1)


class TestGetErrorLog:

    def test_warning(self):
        h = Helper()
        from loguru import logger
        logger.warning('msg')
        assert h.get_error_log() == ''

    def test_error(self):
        h = Helper()
        from loguru import logger
        logger.error('msg')
        assert h.get_error_log() != ''

    def test_critical(self):
        h = Helper()
        from loguru import logger
        logger.critical('msg')
        assert h.get_error_log() != ''
