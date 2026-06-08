from random import randint

#from twilio.rest import Client


class SMSSender:
    def __init__(self):
        """
        This class represents the SMS sender.
        It starts by generating the SMS code.
        """

        self.code = []

        for i in range(4):
            self.code.append(f"{randint(1,9)}")

        self.code = "".join(self.code)

    def send(self, phone_number):
        """
        It sends the code to the passed phone number.
        """

        print(f"Seu código do AgroBook: {self.code}")

        """
        account_sid = 'our_account_sid'
        auth_token = 'our_auth_token'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f'Seu código do AgroBook: {self.code}',
            from_='+12345678901', # Our phone number in Twilio
            to=phone_number   # Farmer's phone number
        )

        print(message.sid)
        """