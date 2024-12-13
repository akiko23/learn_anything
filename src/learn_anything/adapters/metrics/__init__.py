from prometheus_client import Counter, Histogram


REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'path'])
INTEGRATION_METHOD_DURATION = Histogram('integration_method_duration_seconds', 'Time spent in integration methods')
BROKER_MESSAGES_PRODUCED = Counter('rabbitmq_messages_produced_total', 'Total messages produced to RabbitMQ')
BROKER_MESSAGES_CONSUMED = Counter('rabbitmq_messages_consumed_total', 'Total messages consumed from RabbitMQ')
