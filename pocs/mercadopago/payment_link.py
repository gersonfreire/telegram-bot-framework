#!/usr/bin/env python3

# pip install mercadopago

import mercadopago
import dotenv
import os

YOUR_PUBLIC_KEY=os.getenv("YOUR_PUBLIC_KEY")
YOUR_PRIVATE_KEY=os.getenv("YOUR_PRIVATE_KEY")

# Replace 'YOUR_PUBLIC_KEY' and 'YOUR_PRIVATE_KEY' with your actual keys
sdk = mercadopago.SDK(YOUR_PUBLIC_KEY, YOUR_PRIVATE_KEY)

data = {
    "items": [
        {
            "title": "Product Name",
            "quantity": 1,
            "unit_price": 100
        }
    ],
    "back_urls": {
        "success": "http://your-website.com/success",
        "failure": "http://your-website.com/failure"
    },
    "notification_url": "http://your-website.com/notification"
}

preference = sdk.preference.create(data)

print(preference['response']['sandbox_init_point'])