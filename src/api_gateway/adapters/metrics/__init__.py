from prometheus_client import Counter

REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'path'])
BROKER_MESSAGES_PRODUCED = Counter('rabbitmq_messages_produced_total', 'Total messages produced to RabbitMQ')
