from typing import Callable
import boto3
import os
import threading


sqs = boto3.client('sqs',
                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                   aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                   region_name=os.getenv('AWS_DEFAULT_REGION')
                   )

run_thread = True

def _listen_queue_messages(on_message: Callable):
    global run_thread

    while run_thread:
        # Get message from queue
        queue_response = sqs.receive_message(
            QueueUrl=os.getenv('AWS_QUEUE_URL'),
            WaitTimeSeconds=5
        )

        # If message exists, process it
        if queue_response is not None and 'Messages' in queue_response:
            for message in queue_response['Messages']:
                # Call the callback with the message
                on_message(message)
                # Delete the message from the queue
                sqs.delete_message(
                    QueueUrl=os.getenv('AWS_QUEUE_URL'),
                    ReceiptHandle=message['ReceiptHandle']
                )

def start_listening(on_message: Callable):
    print("Starting listener thread...")
    threading.Thread(target=lambda: _listen_queue_messages(on_message)).start()
    print("Listener thread started.")

def stop_listening():
    global run_thread
    run_thread = False
    print("Listener thread stopped.")
