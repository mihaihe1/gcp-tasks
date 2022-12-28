# pylint: disable=C0301
# pylint: disable=W1203
from os import getenv
import logging
import time
import json
from datetime import datetime, time as date_time
import requests

from google.cloud import bigquery
from google.cloud.pubsub_v1 import PublisherClient

logging.basicConfig(level=logging.INFO)

PROJECT_ID = getenv("PROJECT_ID")
OUTPUT_TABLE = getenv("OUTPUT_TABLE")
TOPIC_ID = getenv("TOPIC_ID")


class PubSubPublisher:
    def __init__(self, publisher: PublisherClient,
                 project_id: str,
                 topic_id: str, ):
        self._publisher = publisher
        self._topic_path = publisher.topic_path(project_id, topic_id)

    def publish(self, data: bytes) -> bool:
        try:

            future = self._publisher.publish(self._topic_path,
                                             data)
            try:
                future.result()
                logging.info("Successfully published to topic")
                return True
            except RuntimeError as err:
                logging.error("An error occurred during "  # pylint: disable=E1205
                              "publishing the message",
                              str(err))
                return False

        except Exception as err:  # pylint: disable=broad-except
            logging.error(f"Unexpected error: {str(err)}")  # pylint: disable=E1205
            return False


def convert_timestamp_to_sql_date_time(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))


def store_data_into_bq(dataset, timestamp, event):
    try:
        query = f"INSERT INTO `{dataset}` VALUES ('{timestamp}', '{event}')"

        bq_client = bigquery.Client()
        query_job = bq_client.query(query=query)
        query_job.result()

        logging.info(f"Query results loaded to the {dataset}")
    except AttributeError as error:
        logging.error(f"Query job could not be completed: {error}")


def store_data_into_pubsub(event):
    ps_client = PublisherClient()
    ps_object = PubSubPublisher(ps_client, PROJECT_ID, TOPIC_ID)
    data = bytes(event, 'utf-8')
    ps_object.publish(data)


def main(request):
    logging.info("Request: %s", request)

    if request.method == "POST":  # currently function works only with POST method

        event: str
        try:
            event = json.dumps(request.json)
        except TypeError as error:
            return {"error": f"Function only works with JSON. Error: {error}"}, 415, \
                {'Content-Type': 'application/json; charset=utf-8'}

        timestamp = time.time()
        dataset = f"{PROJECT_ID}.{OUTPUT_TABLE}"
        store_data_into_bq(dataset,
                           convert_timestamp_to_sql_date_time(timestamp),
                           event)

        store_data_into_pubsub(event)

        return "", 204

    return {"error": f"{request.method} method is not supported"}, 500, \
        {'Content-Type': 'application/json; charset=utf-8'}
