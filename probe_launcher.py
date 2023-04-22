from sys import stderr
import traceback
import docker
import os
import uuid

from model.request import Request
from request_parser import parse_request

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

def handle_probe_start_request(probe_request: Request):
    try:

        probe_request = parse_request(probe_request)
        print("Starting probe [{} - {}] with target {}".format(probe_request.name, probe_request.id, probe_request.target))

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
    except Exception:
        print("===========\nERROR : ", end="")
        print(traceback.format_exc())
