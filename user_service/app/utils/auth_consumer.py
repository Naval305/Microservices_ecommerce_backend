import json
import os
import pika
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.config import (
    rabbitmq_host,
    rabbitmq_port,
    rabbitmq_user,
    rabbitmq_password,
    rabbitmq_token_exchange,
    rabbitmq_token_queue,
    rabbitmq_token_routing_key,
    rabbitmq_feedback_exchange,
    rabbitmq_feedback_queue,
    rabbitmq_feedback_routing_key,
)
from app.utils.users import authenticate


class AuthenticateToken:
    def __init__(self) -> None:
        credentials = pika.PlainCredentials(
            username=rabbitmq_user, password=rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=rabbitmq_token_exchange)
        self.channel.queue_declare(queue=rabbitmq_token_queue)
        self.channel.queue_bind(
            queue=rabbitmq_token_queue,
            exchange=rabbitmq_token_exchange,
            routing_key=rabbitmq_token_routing_key,
        )

        self.channel.exchange_declare(exchange=rabbitmq_feedback_exchange)
        self.channel.queue_declare(queue=rabbitmq_feedback_queue)
        self.channel.queue_bind(
            exchange=rabbitmq_feedback_exchange,
            queue=rabbitmq_feedback_queue,
            routing_key=rabbitmq_feedback_routing_key,
        )

    def callback(self, channel, method, properties, body) -> None:
        data, status = authenticate(body)
        self.channel.basic_publish(
            exchange=rabbitmq_feedback_exchange,
            routing_key=rabbitmq_feedback_routing_key,
            body=json.dumps(data),
        )

    def consume(self) -> None:
        self.channel.basic_consume(
            queue=rabbitmq_token_queue, on_message_callback=self.callback, auto_ack=True
        )


        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
        except Exception as e:
            self.connection.close()
            raise


AuthenticateToken().consume()
