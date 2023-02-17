import logging
import re


class RedactionFilter(logging.Filter):
    """A logging filter to redact confidential info"""

    REDACT_SENSITIVE_LOGS = [
        r"(Bearer )[^\']+",
        r"(\'attach\', \')[^\']+",
        r"(\'machineToken\': \')[^\']+",
        r"(\'token\': \')[^\']+",
        r"(\'X-aws-ec2-metadata-token\': \')[^\']+",
        r"(.*\[PUT\] response.*api/token,.*data: ).*",
        r"(https://bearer:)[^\@]+",
        r"(/snap/bin/canonical-livepatch\s+enable\s+)[^\s]+",
        r"(Contract\s+value\s+for\s+'resourceToken'\s+changed\s+to\s+).*",
        r"(\'resourceToken\': \')[^\']+",
        r"(\'contractToken\': \')[^\']+",
        r"(https://contracts.canonical.com/v1/resources/"
        r"livepatch\?token=)[^\s]+",
        r"(\"identityToken\": \")[^\"]+",
        r"(response:\s+http://metadata/computeMetadata/v1/instance/"
        "service-accounts.*data: ).*",
        r"(\'token\': \')[^\']+",
        r"(\'userCode\': \')[^\']+",
        r"(\'magic_token=)[^\']+",
    ]

    def redact_log(self, content: str) -> str:
        redacted_log = content
        for redact_regex in RedactionFilter.REDACT_SENSITIVE_LOGS:
            redacted_log = re.sub(
                redact_regex, r"\g<1><REDACTED>", redacted_log
            )
        return redacted_log

    def filter(self, record: logging.LogRecord):
        record.msg = self.redact_log(record.msg)
        return True
