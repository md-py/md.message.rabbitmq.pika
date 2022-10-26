import typing
import threading
import queue
import time

import pika
import pika.channel

import md.message


# Meta
__author__ = 'https://md.land/md'
__version__ = '0.1.0'
__all__ = (
    # Meta
    '__author__',
    '__version__',
    # Contract
    'Message',
    'Send',
    'Consumer',
    'Receive',
)


# Contract
class Message(md.message.MessageInterface):
    def __init__(
        self,
        channel: pika.channel.Channel,
        method_frame: pika.spec.Basic.Deliver,
        header_frame: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        self.channel = channel
        self.method_frame = method_frame
        self.header_frame = header_frame
        self.body = body

    def get_payload(self) -> bytes:
        return self.body


class Send(md.message.SendInterface):
    def __init__(
        self,
        connection: pika.BlockingConnection,
        exchange: str,
        routing_key: str,
    ) -> None:
        self._connection = connection  # pika.connection.Connection
        self._exchange = exchange
        self._routing_key = routing_key
        self._channel = self._connection.channel()

    def send(self, message: md.message.MessageInterface) -> None:
        if not self._channel.is_open:  # sometimes channel may be closed
            self._channel = self._connection.channel()

        self._connection.add_callback_threadsafe(
            lambda: self._channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._routing_key,
                body=message.get_payload(),
            )
        )


class Consumer:
    def __init__(
        self,
        connection: pika.BlockingConnection,
        internal_queue: queue.Queue,
        queue_name: str,
        prefetch_count: int,
        queue_durable: bool = True,
        message_requeue: bool = True,
    ) -> None:
        self._connection = connection  # pika.connection.Connection
        self._internal_queue = internal_queue
        self._queue_name = queue_name
        self._prefetch_count = prefetch_count
        self._queue_durable = queue_durable
        self._message_requeue = message_requeue

        self._channel: typing.Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def run(self) -> None:  # sync method
        if self._channel:
            self._channel.close()

        self._channel = self._connection.channel()

        try:
            self._channel.queue_declare(queue=self._queue_name, durable=self._queue_durable)
            self._channel.basic_qos(prefetch_count=self._prefetch_count)
            self._channel.basic_consume(queue=self._queue_name, on_message_callback=self._handle)
            self._channel.start_consuming()
        finally:
            # e.g. channel has stopped consuming
            # before channel close, await consumed messages processing finishing
            time.sleep(2.0)  # todo `self._internal_queue.join()`  # wait until all tasks done, but no longer 3 secs
            if self._channel.is_open:
                self._channel.close()
            # there is no connection management, because it could be reused outside (for publishing in example)

    def stop(self) -> None:
        if self._channel.is_closed:
            return  # do nothing, probably already stopped

        if self._connection.is_open:
            self._connection.add_callback_threadsafe(self._channel.stop_consuming)

    def _handle(
        self,
        channel: pika.channel.Channel,
        method_frame: pika.spec.Basic.Deliver,
        header_frame: pika.spec.BasicProperties,
        body: typing.Any
    ) -> None:
        assert isinstance(body, bytes)
        self._internal_queue.put(item=Message(
            channel=channel,
            method_frame=method_frame,
            header_frame=header_frame,
            body=body,
        ))

    def accept(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver) -> None:
        if self._connection and self._channel:
            self._connection.add_callback_threadsafe(
                lambda: channel.basic_ack(delivery_tag=method.delivery_tag)
            )

    def reject(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver) -> None:
        if self._connection and self._channel:
            self._connection.add_callback_threadsafe(
                lambda: channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
            )


class Receive(md.message.ReceiveInterface):
    def __init__(self, consumer: Consumer, internal_queue: queue.Queue) -> None:
        self._consumer = consumer
        self._internal_queue = internal_queue
        self._thread = threading.Thread(target=self._consumer.run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        if not self._thread.is_alive():
            return

        self._consumer.stop()
        self._thread.join(timeout=3.0)

    def receive(self) -> typing.Iterable[md.message.MessageInterface]:
        while self._thread.is_alive():  # notice: thread could be restarted or managed outside
            try:
                # do not block forever, for case `self.stop()`
                message = self._internal_queue.get(block=True, timeout=0.3)
                self._internal_queue.task_done()  # actual message processing status is no matter
                yield message
            except queue.Empty:
                continue

    def accept(self, message: Message) -> None:
        self._consumer.accept(channel=message.channel, method=message.method_frame)

    def reject(self, message: Message) -> None:
        self._consumer.reject(channel=message.channel, method=message.method_frame)
