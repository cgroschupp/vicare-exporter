import logging
import os
import signal
import sys
import threading
import dotenv
import click

from prometheus_client import REGISTRY, start_http_server
from PyViCare.PyViCare import PyViCare

from vicare_exporter import LOGGER, ViCareCollector
@click.command()
@click.option('--username',  help='vicare username', envvar="VICARE_USERNAME", required=True)
@click.option('--password',  help='vicare password', envvar="VICARE_PASSWORD", required=True)
@click.option('--client-id',  help='vicare client-id', envvar="VICARE_CLIENT_ID", required=True)
@click.option('--metrics-port',  default=9100, help='metrics port', envvar="VICARE_METRICS_PORT")
@click.option('--poll-interval',  default=120, help='poll interval', envvar="VICARE_POLL_INTERVAL")
@click.option('--loglevel',  default="INFO", help='log level', envvar="VICARE_LOGLEVEL")
@click.option('--ignore-device-id',  default=["gateway"], help='ignore device id', multiple=True, envvar="VICARE_IGNORE_DEVICE_IDS")
def run(username, password, client_id, metrics_port, poll_interval, loglevel, ignore_device_id):
    dotenv.load_dotenv()

    logging.basicConfig(
        format="%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s",
        level="INFO",
        stream=sys.stdout,
    )

    LOGGER.setLevel(loglevel)

    vicare = PyViCare()
    vicare.setCacheDuration(0)
    vicare.initWithCredentials(
        username=username,
        password=password,
        client_id=client_id,
        token_file=".vicare_token",
    )

    vicare_collector = ViCareCollector(
        vicare, ignore_device_id, min_fetch_interval_seconds=poll_interval
    )
    LOGGER.info(f"Start serving metrics on port {metrics_port}")
    LOGGER.info(f"Polling vicare features for user {username} every {poll_interval} seconds")
    LOGGER.info(f"Using client id {client_id[:8]}***")
    if ignore_device_id:
        LOGGER.info(f"Ignoring device ids: {ignore_device_id}")

    REGISTRY.register(vicare_collector)
    start_http_server(port=metrics_port)

    stop_event = threading.Event()

    def do_stop(*_):
        LOGGER.info("Received stop signal.")
        stop_event.set()

    signal.signal(signal.SIGINT, do_stop)
    signal.signal(signal.SIGTERM, do_stop)
    stop_event.wait()

if __name__ == "__main__":
    run()