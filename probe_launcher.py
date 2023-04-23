from sys import stderr
import traceback
import docker
import os
import uuid
import threading

from model.request import Request
from request_parser import parse_request

NB_MAX_CONTAINER_IN_PARALLEL = int(os.getenv('NB_MAX_PROBES_IN_PARALLEL')) if os.getenv('NB_MAX_PROBES_IN_PARALLEL') is not None else 5
NB_RUNNING_CONTAINERS = 0
waiting_queue = []


def _wait_container(container, probe_request: Request) -> None:
    global NB_RUNNING_CONTAINERS
    global waiting_queue

    exit_code = container.wait()
    print("Probe {} stopped with code {}".format(probe_request.id, exit_code))
    NB_RUNNING_CONTAINERS -= 1

    if len(waiting_queue) > 0:
        _start_scan(waiting_queue.pop(0))


def _build_container_name(request: Request):
    return "{}_{}_{}".format(request.name, request.id, uuid.uuid4())


def _probe_name_to_image(name: str):
    return "{}:{}".format(os.getenv("DOCKER_IMAGE_REPO"), name)


def _build_probe_env_variables(probe_request: Request):
    more_settings = {
        "PROBE_ID": probe_request.id,
        "TARGET": probe_request.target,

        "AWS_ACCESS_KEY": os.getenv("AWS_ACCESS_KEY"),
        "AWS_SECRET_KEY": os.getenv("AWS_SECRET_KEY"),
        "AWS_QUEUE_URL": os.getenv("AWS_QUEUE_URL"),
        "AWS_QUEUE_RESPONSE_URL": os.getenv("AWS_QUEUE_RESPONSE_URL"),
        "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),

        "MONGO_URL": os.getenv('MONGO_URL'),
        "MONGO_DB": os.getenv("MONGO_DB"),
        "MONGO_COLLECTION": os.getenv("MONGO_COLLECTION"),

        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    }

    try:
        return probe_request.settings | more_settings
    except:
        return more_settings


def _start_scan(probe_request: Request) -> None:
    global NB_RUNNING_CONTAINERS

    print("Starting probe [{} - {}] with target {}".format(
        probe_request.name, probe_request.id, probe_request.target))

    # Deploy docker container
    docker_client = docker.from_env()
    container = docker_client.containers.run(
        image=_probe_name_to_image(probe_request.name),
        name=_build_container_name(probe_request),
        environment=_build_probe_env_variables(probe_request),
        stderr=True,
        stdout=True,
        network="host",
        detach=True
    )

    t = threading.Thread(target=_wait_container, args=[container, probe_request])
    t.start()
    NB_RUNNING_CONTAINERS += 1


def handle_probe_start_request(probe_request: Request):
    try:
        probe_request = parse_request(probe_request)

        if NB_RUNNING_CONTAINERS < NB_MAX_CONTAINER_IN_PARALLEL:
            _start_scan(probe_request)
        else:
            print("Sent probe {} to waiting queue".format(probe_request.id))
            waiting_queue.append(probe_request)

    except Exception:
        print("===========\nERROR : ", end="")
        print(traceback.format_exc())
