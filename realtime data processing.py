from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'], 
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def send_to_kafka(topic, data):
    producer.send(topic, value=data)
    producer.flush()

news_data = {'title': 'Sample Title', 'link': 'http://example.com', 'summary': 'Sample Summary'}
send_to_kafka('news_topic', news_data)
