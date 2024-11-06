# How to Start the Python Embedded HTTP Server and Serve an `index.html` File

Python comes with a simple built-in HTTP server that can be used to serve files from a directory. This is useful for quickly testing web pages or sharing files over a local network.

## Steps to Start the Python HTTP Server

1. **Create an `index.html` File**

   First, create an `index.html` file in the directory you want to serve. For example:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>My Web Page</title>
   </head>
   <body>
       <h1>Welcome to My Web Page</h1>
       <p>This is a simple HTML file served by the Python HTTP server.</p>
   </body>
   </html>```


   ```
2. **Navigate to the Directory**

   Open a terminal or command prompt and navigate to the directory containing the `index.html` file. For example:

```sh
   cd path/to/your/directory
```

3. **Start the Python HTTP Server**

   Depending on your Python version, use one of the following commands to start the HTTP server:

   - For Python 3.x:

     ```sh
     python -m http.server 8000
     ```
   - For Python 2.x:

     ```sh
     python -m SimpleHTTPServer 8000
     ```

   This will start the HTTP server on port 8000. You can change the port number to any available port if needed.
5. **Access the Server**

   Open a web browser and navigate to `http://localhost:8000`. You should see the contents of the `index.html` file displayed in the browser.

That's it! You have successfully started the Python embedded HTTP server and served an `index.html` file.
