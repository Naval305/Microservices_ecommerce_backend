import os
import pika
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from app.config.config import (
    rabbitmq_host,
    rabbitmq_password,
    rabbitmq_port,
    rabbitmq_user,
    rabbitmq_feedback_exchange,
    rabbitmq_feedback_queue,
    rabbitmq_feedback_routing_key,
)


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

        self.channel.exchange_declare(exchange=rabbitmq_feedback_exchange)
        self.channel.queue_declare(queue=rabbitmq_feedback_queue)
        self.channel.queue_bind(
            exchange=rabbitmq_feedback_exchange,
            queue=rabbitmq_feedback_queue,
            routing_key=rabbitmq_feedback_routing_key,
        )

    def callback(self, channel, method, properties, body) -> None:
        from app.utils.redis_config import init_sync_redis
        print(body)
        redis = init_sync_redis()
        redis.set("verified", body, 60)

    def consume(self) -> None:
        self.channel.basic_consume(
            queue=rabbitmq_feedback_queue,
            on_message_callback=self.callback,
            auto_ack=True,
        )
        print("FastAPI Consuming...")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
        except Exception as e:
            print("An error occurred during message consumption: %s", str(e))
            self.connection.close()
            raise


ConnectUserService().consume()
