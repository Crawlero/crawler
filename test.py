import asyncio
from aiokafka import AIOKafkaProducer
import json

KAFKA_INPUT_TOPIC = "crawl_inputs"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"


async def send_job():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        job = {
            "url": "https://www.nbcnews.com/business",
            "schema": {
                "name": "News Teaser Extractor",
                "baseSelector": ".wide-tease-item__wrapper",
                "fields": [
                    {
                        "name": "category",
                        "selector": ".unibrow span[data-testid='unibrow-text']",
                        "type": "text",
                    },
                    {
                        "name": "headline",
                        "selector": ".wide-tease-item__headline",
                        "type": "text",
                    },
                    {
                        "name": "summary",
                        "selector": ".wide-tease-item__description",
                        "type": "text",
                    },
                    {
                        "name": "time",
                        "selector": "[data-testid='wide-tease-date']",
                        "type": "text",
                    },
                    {
                        "name": "image",
                        "type": "nested",
                        "selector": "picture.teasePicture img",
                        "fields": [
                            {"name": "src", "type": "attribute", "attribute": "src"},
                            {"name": "alt", "type": "attribute", "attribute": "alt"},
                        ],
                    },
                    {
                        "name": "link",
                        "selector": "a[href]",
                        "type": "attribute",
                        "attribute": "href",
                    },
                ],
            }
        }
        await producer.send_and_wait(KAFKA_INPUT_TOPIC, job)
        print("Job sent to Kafka")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(send_job())
