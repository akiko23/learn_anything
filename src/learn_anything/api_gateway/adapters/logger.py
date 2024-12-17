import logging.config
from contextlib import suppress
from contextvars import ContextVar

import yaml
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError
from starlette_context.header_keys import HeaderKeys


with open('configs/logging.conf.yml', 'r') as f:
    LOGGING_CONFIG = yaml.full_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        corr_id_from_app_ctx = correlation_id_ctx.get(None)
        if corr_id_from_app_ctx:
            return '[%s] %s' % (corr_id_from_app_ctx, super().format(record))

        with suppress(ContextDoesNotExistError):
            if corr_id := context.get(HeaderKeys.correlation_id, None):
                return '[%s] %s' % (corr_id, super().format(record))

        return super().format(record)


correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id')
logger = logging.getLogger('api_gateway_logger')
