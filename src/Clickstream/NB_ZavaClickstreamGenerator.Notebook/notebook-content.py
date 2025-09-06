# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Installation for kafka-python library (run once)
!pip install kafka-python


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Imports and basic configuration
import json
import uuid
import random
import time
from datetime import datetime, timedelta, timezone
from kafka import KafkaProducer
import numpy as np

# Configurable parameters
EVENTS_PER_SECOND = 10  # Rate of events per second
SIMULATION_HOURS = 8   # Duration to run the simulation in hours

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Kafka Endpoint configuration parameters

# KAFKA_BROKER maps to Bootstrap Server address in the Eventstream
KAFKA_BROKER = ''  # Bootstrap server address

# KAFKA_TOPIC maps to Topic name in the Eventstream
KAFKA_TOPIC = ''  # Kafka topic for event ingestion

# sas_username to be retained as is.
sas_username = '$ConnectionString'

# sas_password maps to Primary Key Connection String in the Eventstream
sas_password = ''

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Constants for simulation
COUNTRIES = [
    {"name": "Germany", "code": "DE"},
    {"name": "Sweden", "code": "SE"},
    {"name": "Estonia", "code": "EE"},
    {"name": "United States", "code": "US"},
    {"name": "United Kingdom", "code": "GB"},
    {"name": "France", "code": "FR"},
    {"name": "Spain", "code": "ES"},
    {"name": "Netherlands", "code": "NL"},
    {"name": "Italy", "code": "IT"},
    {"name": "Poland", "code": "PL"},
]

BROWSING_CATEGORIES = ["Men", "Women", "Kids"]
SNEAKER_CATEGORIES = ["GenZ Pros", "Altars", "Colours"]

REFERRAL_SOURCES = [
    "organic_search", "facebook", "instagram", "tiktok", 
    "pinterest", "twitter", "other_social", "affiliate", 
    "direct", "other"
]

BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
OS = ["Windows", "macOS", "Linux", "Android", "iOS"]
DEVICE_TYPES = ["Desktop", "Mobile", "Tablet"]

USER_ACCOUNT_TYPES = ["guest", "registered"]

# Anomaly config
ANOMALY_CHANCE = 0.01   # 1% events are anomalies approx.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def generate_ip():
    return "{}.{}.{}.{}".format(
        random.randint(1, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(1, 254)
    )

def generate_user_agent():
    return {
        "browser": random.choice(BROWSERS),
        "os": random.choice(OS),
        "device": random.choice(DEVICE_TYPES)
    }

def generate_country():
    return random.choice(COUNTRIES)

def generate_session_id():
    return str(uuid.uuid4())

def generate_referral_source():
    return random.choice(REFERRAL_SOURCES)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

PRODUCTS = []
for cat in BROWSING_CATEGORIES:
    for sneaker_cat in SNEAKER_CATEGORIES:
        for i in range(1, 6):  # 5 products per subcategory
            PRODUCTS.append({
                "product_id": f"{cat[:2].upper()}_{sneaker_cat[:2].upper()}_{i}",
                "category": cat,
                "sneaker_category": sneaker_cat,
                "price": round(random.uniform(70, 250), 2)
            })

def select_random_product():
    return random.choice(PRODUCTS)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Generate timestamps distributed over past 6 months weighted toward recent days
def generate_trending_timestamp():
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=180)  # 6 months ago
    
    # Exponentially weighted days back, capped at 180 days
    days_back = np.random.exponential(scale=30)
    days_back = min(days_back, 180)
    event_time = now - timedelta(days=days_back)
    
    random_seconds = random.randint(0, 86399)
    event_time = event_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=random_seconds)
    return event_time.isoformat()

# Get event type by weekday trend and time-based trends
def event_type_weighted_by_trends(current_time=None):
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    weekday = current_time.weekday()  # 0 = Monday, ..., 6 = Sunday
    
    base_weights = {
        "browse_category": 20,
        "view_product": 20,
        "add_to_cart": 15,
        "remove_from_cart": 10,
        "initiate_checkout": 5,
        "complete_purchase": 5,
        "create_account": 10,
        "subscribe_mailing_list": 7,
        "unsubscribe_mailing_list": 8
    }
    
    # Weekend purchase surge
    if weekday in [5, 6]:
        base_weights["complete_purchase"] *= 2
        base_weights["initiate_checkout"] *= 2
    
    # Monday new signups boost
    if weekday == 0:
        base_weights["create_account"] *= 1.5
    
    # Regional monthly trend (simulate boost in 3rd month)
    month = current_time.month
    if month == ((datetime.now(timezone.utc) - timedelta(days=30*3)).month):
        base_weights["view_product"] *= 1.3
        base_weights["add_to_cart"] *= 1.3
    
    total = sum(base_weights.values())
    normalized_weights = [w / total for w in base_weights.values()]
    event_types = list(base_weights.keys())
    return random.choices(event_types, weights=normalized_weights)[0]

# Occasional anomaly: generate bursts or spikes
def anomaly_event_override():
    anomaly_types = [
        "complete_purchase", 
        "unsubscribe_mailing_list",
        "add_to_cart",
        "remove_from_cart"
    ]
    # Choose a random anomaly with large event count
    return random.choice(anomaly_types)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

EVENT_TYPES = [
    "browse_category", "view_product", "add_to_cart", "remove_from_cart",
    "initiate_checkout", "complete_purchase", "create_account",
    "subscribe_mailing_list", "unsubscribe_mailing_list"
]

def generate_click_path(event_type):
    path = ["home"]
    if event_type in ["browse_category", "view_product", "add_to_cart", "remove_from_cart"]:
        cat = random.choice(BROWSING_CATEGORIES)
        sneaker_cat = random.choice(SNEAKER_CATEGORIES)
        path.extend([f"category_{cat}", f"subcategory_{sneaker_cat}"])
        if event_type in ["view_product", "add_to_cart", "remove_from_cart"]:
            product = select_random_product()
            path.append(f"product_{product['product_id']}")
    elif event_type in ["initiate_checkout", "complete_purchase"]:
        path = ["home", "cart", "checkout"]
    elif event_type == "create_account":
        path = ["home", "signup"]
    elif event_type in ["subscribe_mailing_list", "unsubscribe_mailing_list"]:
        path = ["home", "newsletter"]
    return path

def clean_payload(payload):
    return {k: v for k, v in payload.items() if v is not None}

def generate_event(user_state):
    # Determine if anomaly event triggered
    if random.random() < ANOMALY_CHANCE:
        event_type = anomaly_event_override()
    else:
        # Use trending timestamp and event type weighted by trends
        timestamp = generate_trending_timestamp()
        event_type = event_type_weighted_by_trends(datetime.fromisoformat(timestamp))
    # If no anomaly, generate timestamp now
    if 'timestamp' not in locals():
        timestamp = datetime.now(timezone.utc).isoformat()

    payload = {}
    if event_type == "browse_category":
        payload["category"] = random.choice(BROWSING_CATEGORIES)
        payload["sneaker_category"] = random.choice(SNEAKER_CATEGORIES)
    elif event_type == "view_product":
        product = select_random_product()
        payload.update({
            "product_id": product["product_id"],
            "category": product["category"],
            "sneaker_category": product["sneaker_category"],
            "price": product["price"]
        })
    elif event_type == "add_to_cart":
        product = select_random_product()
        quantity = random.randint(1, 3)
        user_state["cart"][product["product_id"]] = user_state["cart"].get(product["product_id"], 0) + quantity
        payload.update({
            "product_id": product["product_id"],
            "quantity_added": quantity
        })
    elif event_type == "remove_from_cart":
        if not user_state["cart"]:
            return None
        product_id = random.choice(list(user_state["cart"].keys()))
        quantity_removed = random.randint(1, user_state["cart"][product_id])
        user_state["cart"][product_id] -= quantity_removed
        if user_state["cart"][product_id] <= 0:
            del user_state["cart"][product_id]
        payload.update({
            "product_id": product_id,
            "quantity_removed": quantity_removed
        })
    elif event_type == "initiate_checkout":
        if not user_state["cart"]:
            return None
        payload["cart_items"] = sum(user_state["cart"].values())
        payload["cart_total"] = round(sum(
            next(p["price"] for p in PRODUCTS if p["product_id"] == pid) * qty
            for pid, qty in user_state["cart"].items()
        ), 2)
    elif event_type == "complete_purchase":
        if not user_state["cart"]:
            return None
        payload["purchase_id"] = str(uuid.uuid4())
        payload["items_purchased"] = sum(user_state["cart"].values())
        payload["purchase_total"] = round(sum(
            next(p["price"] for p in PRODUCTS if p["product_id"] == pid) * qty
            for pid, qty in user_state["cart"].items()
        ), 2)
        user_state["cart"].clear()
    elif event_type == "create_account":
        payload["account_type"] = user_state["account_type"]
    elif event_type == "subscribe_mailing_list":
        payload["subscribed"] = True
    elif event_type == "unsubscribe_mailing_list":
        payload["subscribed"] = False
    else:
        return None

    payload = clean_payload(payload)

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": user_state["user_id"],
        "session_id": user_state["session_id"],
        "timestamp": timestamp,
        "country": user_state["country"]["name"],
        "country_code": user_state["country"]["code"],
        "referral_source": user_state["referral"],
        "click_path": generate_click_path(event_type),
        "payload": payload,
        "client_info": {
            "ip": user_state["ip"],
            "browser": user_state["client_info"]["browser"],
            "os": user_state["client_info"]["os"],
            "device": user_state["client_info"]["device"]
        }
    }
    return event


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

producer = None

def init_kafka_producer(
    broker, 
    sasl_username=None, 
    sasl_password=None, 
    sasl_mechanism='PLAIN', 
    security_protocol='SASL_SSL'
):
    global producer
    kafka_config = {
        'bootstrap_servers': [broker],
        'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
        'acks': 'all',
        'retries': 3,
    }
    if sasl_username and sasl_password:
        kafka_config.update({
            'security_protocol': security_protocol,
            'sasl_mechanism': sasl_mechanism,
            'sasl_plain_username': sasl_username,
            'sasl_plain_password': sasl_password
        })
    else:
        kafka_config['security_protocol'] = 'PLAINTEXT'
    
    producer = KafkaProducer(**kafka_config)
    print(f"Kafka producer initialized to broker {broker}")

def send_event_to_kafka(event):
    if producer is None:
        raise Exception("Kafka producer not initialized")
    try:
        future = producer.send(KAFKA_TOPIC, event)
        record_metadata = future.get(timeout=10)
        print(f"Event sent to topic {record_metadata.topic} "
              f"partition {record_metadata.partition} offset {record_metadata.offset}")
        producer.flush()
    except Exception as e:
        print(f"Error sending event to Kafka: {e}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def run_event_simulation(
    events_per_second, 
    duration_hours, 
    kafka_send_func=None, 
    print_events=True
):
    total_events = int(events_per_second * 3600 * duration_hours)
    user_states = {}

    def get_or_create_user_state(user_id=None):
        if user_id and user_id in user_states:
            return user_states[user_id]
        user_id = user_id or str(uuid.uuid4())
        session_id = generate_session_id()
        account_type = random.choice(USER_ACCOUNT_TYPES)
        country = generate_country()
        ip = generate_ip()
        client_info = generate_user_agent()
        referral = generate_referral_source()
        state = {
            "user_id": user_id,
            "session_id": session_id,
            "account_type": account_type,
            "country": country,
            "ip": ip,
            "client_info": client_info,
            "referral": referral,
            "cart": {}
        }
        user_states[user_id] = state
        return state

    start_time = time.time()
    for i in range(total_events):
        user_state = get_or_create_user_state()
        event = generate_event(user_state)
        if event is None:
            continue
        
        if print_events:
            print(json.dumps(event))
        
        if kafka_send_func:
            kafka_send_func(event)
        
        elapsed = time.time() - start_time
        expected_elapsed = (i + 1) / events_per_second
        to_sleep = expected_elapsed - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)
        
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1} events, elapsed: {elapsed:.2f} seconds")

    print("Simulation complete.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Initialize Kafka Producer with SASL credentials
init_kafka_producer(KAFKA_BROKER, sas_username, sas_password)

# Run simulation with event sending to Kafka enabled, printing events to notebook
run_event_simulation(
    EVENTS_PER_SECOND,
    SIMULATION_HOURS,
    kafka_send_func=send_event_to_kafka,
    print_events=True
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
