from dotenv import load_dotenv
load_dotenv()

import queue_reader



def __main__():
    queue_reader.start_listening(lambda message: print(message))
    queue_reader.stop_listening()


if __name__ == '__main__':
    try:
        __main__()
    except KeyboardInterrupt:
        queue_reader.stop_listening()
