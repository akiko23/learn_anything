from prometheus_client import Counter, Histogram


INTEGRATION_METHOD_DURATION = Histogram('integration_method_duration_seconds', 'Time spent in integration methods')
TOTAL_MESSAGES_CONSUMED = Counter('rabbitmq_messages_consumed_total', 'Total messages consumed from RabbitMQ')
REQUESTS_TOTAL = Counter('rabbitmq_requests_total', 'Total requests')
