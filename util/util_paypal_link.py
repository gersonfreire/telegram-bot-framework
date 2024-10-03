#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, dotenv
import paypalrestsdk

import util_paypal_receive

dotenv.load_dotenv()

def create_payment(
    return_url="http://localhost:5000/payment/execute", 
    cancel_url="http://localhost:5000/payment/cancel", 
    total="5.00", 
    currency="BRL", 
    description="This is the payment transaction description.",
    client_id = os.getenv("PAYPAL_CLIENT_ID") ,
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    ): 

    try:  

        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": client_id,
            "client_secret": client_secret
        })
        
        # Step 3: Create a Payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": "5.00",
                        "currency": "BRL",
                        "quantity": 1}]},
                "amount": {
                    "total": total,
                    "currency": currency},
                "description": description}]})

        # Step 4: Generate the Payment Link
        if payment.create():
            print("Payment created successfully")
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    print("Redirect for approval: %s" % (approval_url))
                    
        else:
            print(payment.error)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    
    util_paypal_receive.main()
    
    create_payment()      