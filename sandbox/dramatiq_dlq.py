import dramatiq
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker

stub_broker = StubBroker()
dramatiq.set_broker(stub_broker)


@dramatiq.actor(max_retries=3, min_backoff=100)
def hello_world(x: str):
    print(f"-> Received: {x}. Attempting to process...")
    raise ValueError("I am a simulated error!")


if __name__ == "__main__":
    print("---starting worker---")

    worker = Worker(stub_broker)
    worker.start()

    print("---sending message---")

    hello_world.send("hello world")

    stub_broker.join(hello_world.queue_name, fail_fast=False)
    worker.join()

    print("---Cheking Dead Letters (DLQ)--")

    print(f"Numbers of dead letters: {len(stub_broker.dead_letters)}")
    for dead_letter in stub_broker.dead_letters:
        print(f"Message ID: {dead_letter.message_id}")
        print(f"Exception: {dead_letter._exception}")

    print("--Stopping Worker---")
    worker.stop()
