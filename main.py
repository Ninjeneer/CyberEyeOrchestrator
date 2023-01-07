from dotenv import load_dotenv
load_dotenv()

import queue_reader
from probe_launcher import handle_probe_start_request


def __main__():
    queue_reader.start_listening(lambda message: handle_probe_start_request(message['Body']))


if __name__ == '__main__':
    try:
        __main__()
    except KeyboardInterrupt:
        queue_reader.stop_listening()
