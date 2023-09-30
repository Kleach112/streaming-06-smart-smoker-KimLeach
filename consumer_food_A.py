"""
Author: Kim Leach
Date: 09/29/2023

This script is tailored to monitor the temperature of Food A. It subscribes to the '02-food-A' queue 
from RabbitMQ for temperature readings. If the temperature change for Food A is 1°F or less over 
a span of 10 minutes (20 readings), a stall alert is generated. This alert is both displayed on the console 
and emailed to the designated recipient.
"""

import pika
import smtplib
from email.message import EmailMessage
from collections import deque
from datetime import datetime

# Connection and queue declaration for RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='02-food-A', durable=True)

food_a_temps = deque(maxlen=20)

def food_a_callback(ch, method, properties, body):
    global food_a_temps
    
    # Split the message into parts (datetime and temperature)
    parts = body.decode().split(',')
    
    if len(parts) != 2:
        print("Received an invalid message format. Skipping.")
        return
    
    dt, temp = parts
    current_temp = float(temp)
    food_a_temps.append(current_temp)
    
    if len(food_a_temps) == 20 and abs(food_a_temps[0] - food_a_temps[-1]) <= 1:
        alert_msg = f"Food Stall Alert for Food A! Temperature change is 1°F or less at {dt}"
        print(alert_msg)

channel.basic_consume(queue='02-food-A', on_message_callback=food_a_callback, auto_ack=True)
print(' [*] Waiting for Food A messages. To exit press CTRL+C')
channel.start_consuming()
