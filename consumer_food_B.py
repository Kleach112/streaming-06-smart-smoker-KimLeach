"""
Author: Kim Leach
Date: 09/29/2023

This script is set up to monitor the temperature of Food B. It connects to the '03-food-B' queue in RabbitMQ 
for temperature data. If the temperature variation for Food B is 1°F or less within a time frame of 10 minutes 
(20 readings), a stall alert is triggered. This alert is then printed to the console and also sent as an email 
to the given recipient.
"""

import pika
import smtplib
from email.message import EmailMessage
from collections import deque
from datetime import datetime

# Connection and queue declaration for RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='03-food-B', durable=True)

food_b_temps = deque(maxlen=20)

def food_b_callback(ch, method, properties, body):
    global food_b_temps
    dt, temp = body.decode().split(',')
    current_temp = float(temp)
    food_b_temps.append(current_temp)
    
    if len(food_b_temps) == 20 and abs(food_b_temps[0] - food_b_temps[-1]) <= 1:
        alert_msg = f"Food Stall Alert for Food B! Temperature change is 1°F or less at {dt}"
        print(alert_msg)

channel.basic_consume(queue='03-food-B', on_message_callback=food_b_callback, auto_ack=True)
print(' [*] Waiting for Food B messages. To exit press CTRL+C')
channel.start_consuming()
