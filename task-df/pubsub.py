import json
import time
from datetime import datetime
import random
from google.auth import jwt
from google.cloud import pubsub_v1
import datetime

# --- Base variables and auth path
CREDENTIALS_PATH = "task-cf-370908-b6c7b96def5c.json"
PROJECT_ID = "task-cf-370908"
TOPIC_ID = "topic"
MAX_MESSAGES = 5
MAX_ERRORS = 2


# --- PubSub Utils Classes
class PubSubPublisher:
    def __init__(self, credentials_path, project_id, topic_id):
        credentials = jwt.Credentials.from_service_account_info(
            json.load(open(credentials_path)),
            audience="https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
        )
        self.project_id = project_id
        self.topic_id = topic_id
        self.publisher = pubsub_v1.PublisherClient(credentials=credentials)
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)

    def publish(self, data: str):
        result = self.publisher.publish(self.topic_path, data.encode("utf-8"))
        return result


# --- Main publishing script
def main():
    i = 0
    publisher = PubSubPublisher(CREDENTIALS_PATH, PROJECT_ID, TOPIC_ID)

    err_idx = set()

    while len(err_idx) < MAX_ERRORS:
        err_idx.add(random.randint(0, MAX_MESSAGES-1))

    while i < MAX_MESSAGES:
        now = datetime.datetime.utcnow()
        if i in err_idx:
            data = {
                "message": f"message-{i}",
                "number_int": "not an int",
                "number_float": random.random()
            }
        else:
            data = {
                "message": f"message-{i}",
                "number_int": random.randint(0, 10),
                "number_float": random.random(),
                "timestamp": now.strftime('%Y-%m-%d %H:%M:%S')
            }
        publisher.publish(json.dumps(data))
        time.sleep(1)
        i += 1


if __name__ == "__main__":
    main()
