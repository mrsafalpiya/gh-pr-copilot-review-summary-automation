import pika, sys, os
from dotenv import load_dotenv
from script import execute
import json

load_dotenv()

QUEUE_NAME = "gh-pr-copilot-review-summary"


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", 5672)),
            credentials=pika.PlainCredentials(
                os.getenv("RABBITMQ_USER", "user"),
                os.getenv("RABBITMQ_PASS", "password"),
            ),
        )
    )
    channel = connection.channel()

    # channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        body_dict = json.loads(str(body, "utf-8"))
        type = body_dict["type"]
        pr_link = body_dict["pr_link"]
        print(f" [x] Processing {type} - {pr_link}")

        execute(pr_link, type == "opened")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
