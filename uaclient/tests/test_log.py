import logging

import pytest

from uaclient import log as pro_log

LOG = logging.getLogger("uaclient.test.test_log")


class TestLogger:
    @pytest.mark.parametrize("caplog_text", [logging.INFO], indirect=True)
    def test_unredacted_text(self, caplog_text):
        text = "Bearer SEKRET"
        LOG.info(text)
        log = caplog_text()
        assert text in log

    @pytest.mark.parametrize("caplog_text", [logging.INFO], indirect=True)
    def test_redacted_text(self, caplog_text):
        text = "Bearer SEKRET"
        redacted_text = "Bearer <REDACTED>"
        LOG.addFilter(pro_log.RedactionFilter())
        LOG.info(text)
        log = caplog_text()
        assert redacted_text in log
