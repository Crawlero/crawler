import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
from aiokafka import AIOKafkaConsumer

KAFKA_TOPIC = "crawl_jobs"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9093"


async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="crawler_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            job = json.loads(msg.value)
            url = job.get("url")
            schema_str = job.get("schema")
            if not url or not schema_str:
                print("Invalid job received")
                continue

            await crawl(url, schema_str)
    finally:
        await consumer.stop()


async def crawl(url, schema):
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy,
            bypass_cache=True,
        )
        assert result.success, "Failed to crawl the page"
        print("\n_\n")

        print("Extracted data:")
        items = json.loads(result.extracted_content)
        print(json.dumps(items[0], indent=2))


async def main():
    await consume()

if __name__ == "__main__":
    asyncio.run(main())
