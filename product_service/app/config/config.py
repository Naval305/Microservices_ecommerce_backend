import os

from dotenv import load_dotenv


load_dotenv()

# mongodb
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
cluster_name = os.getenv("CLUSTER_NAME")


# redis
redis_host = os.getenv("REDIS_HOST")

# rabbitmq
rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_port = os.getenv("RABBITMQ_PORT")
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

rabbitmq_token_exchange = os.getenv("RABBITMQ_TOKEN_EXCHANGE")
rabbitmq_token_queue = os.getenv("RABBITMQ_TOKEN_QUEUE")
rabbitmq_token_routing_key = os.getenv("RABBITMQ_TOKEN_ROUTING_KEY")

rabbitmq_feedback_exchange = os.getenv("RABBITMQ_FEEDBACK_EXCHANGE")
rabbitmq_feedback_queue = os.getenv("RABBITMQ_FEEDBACK_QUEUE")
rabbitmq_feedback_routing_key = os.getenv("RABBITMQ_FEEDBACK_ROUTING_KEY")
