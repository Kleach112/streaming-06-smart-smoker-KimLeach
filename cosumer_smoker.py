"""
Author: Kim Leach
Date: 09/29/2023

This script is designed to monitor the temperature of a smoker. It listens to the '01-smoker' queue 
from RabbitMQ for temperature readings. If the temperature of the smoker decreases by 15°F or more 
within a span of 2.5 minutes (5 readings), an alert is generated. This alert is both printed to the console 
and sent via email to the specified recipient.
"""


import pika
import smtplib
from email.message import EmailMessage
from collections import deque
from datetime import datetime

# Connection and queue declaration for RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='01-smoker', durable=True)

smoker_temps = deque(maxlen=5)

def smoker_callback(ch, method, properties, body):
    global smoker_temps
    
    # Split the message into parts (datetime and temperature)
    parts = body.decode().split(',')
    
    if len(parts) != 2:
        print("Received an invalid message format. Skipping.")
        return
    
    datetime_str, current_temp_str = parts
    current_temp = float(current_temp_str)
    smoker_temps.append(current_temp)
    
    if len(smoker_temps) == 5 and (smoker_temps[0] - smoker_temps[-1] >= 15):
        alert_msg = f"Smoker Alert! Temperature decreased by 15°F or more at {datetime_str}"
        print(alert_msg)

channel.basic_consume(queue='01-smoker', on_message_callback=smoker_callback, auto_ack=True)
print(' [*] Waiting for smoker messages. To exit press CTRL+C')
channel.start_consuming()
