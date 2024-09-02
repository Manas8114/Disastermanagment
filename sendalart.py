from twilio.rest import Client

account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

def send_alert(message, phone_number):
    client.messages.create(
        body=message,
        from_='+your_twilio_phone_number',
        to=phone_number
    )
    print(f"Alert sent to {phone_number}")

send_alert('Disaster alert: Flood in XYZ region. Take immediate precautions!', '+1234567890')
