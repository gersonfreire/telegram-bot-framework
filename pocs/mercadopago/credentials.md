To generate public and private API keys from your Mercado Pago account settings, follow these steps:

1. **Log in to Mercado Pago**:

   - Go to the [Mercado Pago Developer Portal](https://www.mercadopago.com.ar/developers/en/guides/overview).
   - Log in with your Mercado Pago account credentials.
2. **Navigate to Your Account Settings**:

   - Once logged in, click on your profile icon or name in the top-right corner.
   - Select "Account Settings" or "Settings" from the dropdown menu.
3. **Access API Credentials**:

   - In the account settings, look for a section labeled "Credentials" or "API Credentials".
   - Click on it to access your API keys.
4. **Generate API Keys**:

   - You should see options to generate or view your public and private API keys.
   - If you don't have keys yet, there will be a button to generate new keys.
   - Click on "Generate" or "Create" to get your public and private API keys.
5. **Copy and Save Your Keys**:

   - Once generated, copy the public and private API keys.
   - Save them securely, as you will need them to authenticate your API requests.

### Example

Here is an example of how to use the generated API keys in your Python code:

```python
import mercadopago

# Replace 'YOUR_PUBLIC_KEY' and 'YOUR_PRIVATE_KEY' with your actual keys
sdk = mercadopago.SDK("YOUR_PUBLIC_KEY", "YOUR_PRIVATE_KEY")

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
```

### Summary

- **Log in** to the Mercado Pago Developer Portal.
- **Navigate** to "Account Settings" and then to "API Credentials".
- **Generate** your public and private API keys.
- **Copy and save** the keys securely.
- **Use** the keys in your Python code to authenticate API requests.
