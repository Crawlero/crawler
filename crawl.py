import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

KAFKA_INPUT_TOPIC = "crawl_inputs"
KAFKA_RESULT_TOPIC = "crawl_results"
KAFKA_ERROR_TOPIC = "crawl_errors"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"


async def consume(consumer, producer):
    await consumer.start()
    try:
        async for msg in consumer:
            headers = msg.headers

            job = json.loads(msg.value)
            url = job.get("url")
            schema_str = job.get("schema")
            if not url or not schema_str:
                print("Invalid job received")
                continue

            try:
                await crawl(job, producer, headers)
            except Exception as e:
                print(f"Error processing job: {e}")
                await push_error({"input": job, "error": str(e)}, producer, headers)
    finally:
        await consumer.stop()


async def crawl(input, producer, headers):
    url = input.get("url")
    schema = input.get("schema")

    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy,
            bypass_cache=True,
        )
        if not result.success:
            await push_error({"input": input, "error": result.error}, producer)
            return

        items = json.loads(result.extracted_content)
        await push_result({"input": input, "result": items}, producer, headers)


async def push_result(result, producer, headers):
    await producer.send_and_wait(
        KAFKA_RESULT_TOPIC,
        json.dumps(result).encode('utf-8'),
        headers=list(headers)
    )


async def push_error(error, producer, headers):
    await producer.send_and_wait(
        KAFKA_ERROR_TOPIC,
        json.dumps(error).encode('utf-8'),
        headers=list(headers)
    )


async def main():
    consumer = AIOKafkaConsumer(
        KAFKA_INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="crawler_group"
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    try:
        await consume(consumer, producer)
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
