import pymongo
from pymongo import MongoClient
import re  # Import regular expressions library for parsing

# Establish MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
source_collection = db['social_media_posts']  # Fetch data from the 'social_media_posts' collection
target_collection = db['severity']  # Target collection to save the results

def fetch_summaries():
    """
    Fetches all summaries from the MongoDB collection.
    """
    summaries = []
    ids = []
    for document in source_collection.find({}, {"summary": 1, "_id": 1}):
        summaries.append(document['summary'])
        ids.append(document['_id'])
    return summaries, ids

def extract_data_from_summary(summary):
    """
    Extracts relevant data from a summary text.

    Parameters:
    - summary: The text summary to parse

    Returns:
    - A dictionary with extracted values: loss_of_life, property_damage, duration, resource_utilization
    """
    # Use regular expressions to extract the numbers related to specific keywords
    loss_of_life = int(re.search(r'(\d+)\s*(?:deaths|lives lost|fatalities)', summary).group(1)) if re.search(r'(\d+)\s*(?:deaths|lives lost|fatalities)', summary) else 0
    property_damage_match = re.search(r'\$?(\d+(?:\.\d+)?)\s*(million)?\s*(?:property damage|damages)', summary, re.IGNORECASE)
    property_damage = float(property_damage_match.group(1)) * (1000000 if property_damage_match and property_damage_match.group(2) else 1) if property_damage_match else 0
    duration = int(re.search(r'(\d+)\s*(?:days|weeks|hours|years|min|sec)', summary).group(1)) if re.search(r'(\d+)\s*(?:days|weeks|hours|years|min|sec)', summary) else 0
    resource_utilization = int(re.search(r'(\d+)\s*/\s*100\s*resources?', summary).group(1)) if re.search(r'(\d+)\s*/\s*100\s*resources?', summary) else 0

    return {
        'loss_of_life': loss_of_life,
        'property_damage': property_damage,
        'duration': duration,
        'resource_utilization': resource_utilization
    }

def calculate_severity_score(loss_of_life, property_damage, duration, resource_utilization):
    """
    Calculates the disaster severity score based on multiple factors.

    Parameters:
    - loss_of_life: Number of lives lost
    - property_damage: Estimated property damage in USD
    - duration: Duration of the disaster in days
    - resource_utilization: Resource utilization score (0 to 100)

    Returns:
    - severity_score: Computed severity score (0 to 100)
    """
    # Define scoring ranges for each factor
    life_score = min(loss_of_life / 1000 * 100, 100)  # Score based on lives lost (cap at 100)
    property_score = min(property_damage / 1000000 * 100, 100)  # Score based on property damage in USD (cap at 100 million)
    duration_score = min(duration / 30 * 100, 100)  # Score based on duration in days (cap at 100)
    resource_score = min(resource_utilization, 100)  # Resource utilization score (0 to 100)

    # Define weights for each factor
    weight_life = 35
    weight_property = 2.5
    weight_duration = 0.75
    weight_resource = .15

    # Calculate the weighted severity score
    severity_score = (weight_life * life_score) + \
                     (weight_property * property_score) + \
                     (weight_duration * duration_score) + \
                     (weight_resource * resource_score)

    return severity_score

def fetch_disaster_data_and_calculate_score(post_id):
    """
    Fetches disaster data from the MongoDB collection, extracts relevant data, and calculates the severity score.
    """
    summaries, ids = fetch_summaries()  # Fetch summaries and their document IDs

    # Iterate through each summary and its corresponding ID
    for summary, doc_id in zip(summaries, ids):
        # Extract data from summary
        extracted_data = extract_data_from_summary(summary)

        # Calculate severity score
        severity_score = calculate_severity_score(
            extracted_data['loss_of_life'],
            extracted_data['property_damage'],
            extracted_data['duration'],
            extracted_data['resource_utilization']
        )

        # Skip processing if the severity score is 0.00
        if severity_score == 0.00:
            print(f"Skipping Disaster ID: {doc_id} due to a severity score of 0.00")
            continue

        # Save the calculated severity score and extracted data to the 'severity' collection
        target_collection.update_one(
            {'_id': doc_id},
            {'$set': {
                'severity_score': severity_score,
                'summary': summary,
                'loss_of_life': extracted_data['loss_of_life'],
                'property_damage': extracted_data['property_damage'],
                'duration': extracted_data['duration'],
                'resource_utilization': extracted_data['resource_utilization']
            }},
            upsert=True 
        )

        print(f"Disaster ID: {doc_id}, Severity Score: {severity_score:.2f}/100, Post ID: {post_id}")

def run_multiple_times(n):
    """
    Runs the severity calculation function n times with incremented post_id.
    """
    for i in range(n):
        print(f"Running iteration {i+1} of {n}")
        post_id = i + 1
        fetch_disaster_data_and_calculate_score(post_id)
        print(f"Completed iteration {i+1} of {n}")

if __name__ == "__main__":
    n = 108
    run_multiple_times(n)
