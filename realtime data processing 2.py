import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'news_topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='news-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    news_data = message.value
    print(f"Processing news: {news_data['title']}")
