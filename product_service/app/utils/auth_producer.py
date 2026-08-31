import json
import time

from fastapi import Request
import pika

from app.config.config import (
    rabbitmq_host,
    rabbitmq_password,
    rabbitmq_port,
    rabbitmq_user,
    rabbitmq_token_exchange,
    rabbitmq_token_queue,
    rabbitmq_token_routing_key,
)
from app.utils.utils import get_authentication


class ConnectUserService:
    def __init__(self) -> None:
        credentials = pika.PlainCredentials(
            username=rabbitmq_user, password=rabbitmq_password
        )
        self.parameters = pika.ConnectionParameters(
            host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=rabbitmq_token_exchange)
        self.channel.queue_declare(queue=rabbitmq_token_queue)
        self.channel.queue_bind(
            queue=rabbitmq_token_queue,
            exchange=rabbitmq_token_exchange,
            routing_key=rabbitmq_token_routing_key,
        )


    def publish_token_to_queue(self, token):
        breakpoint()
        self.channel.basic_publish(
            exchange=rabbitmq_token_exchange,
            routing_key=rabbitmq_token_routing_key,
            body=json.dumps({"Authorization": token.credentials}),
        )
        return get_authentication()
