import argparse
import json
import sys
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from importlib import import_module
import uuid


class LambdaHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, handler_func, *args, **kwargs):
        self.handler_func = handler_func
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()

    def do_OPTIONS(self):
        # Handle CORS preflight requests directly
        self.send_response(200)

        # Add CORS headers for localhost requests
        origin = self.headers.get("Origin", "")
        if "localhost" in origin or "127.0.0.1" in origin:
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "http://localhost:*")

        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept, Origin")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Max-Age", "86400")

        self.end_headers()

    def _handle_request(self):
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""

            # Parse URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            # Convert query params to Lambda format
            query_string_params = {}
            for key, values in query_params.items():
                query_string_params[key] = ",".join(values) if len(values) > 1 else values[0]

            # Build Lambda event
            event = {
                "version": "2.0",
                "routeKey": "$default",
                "rawPath": parsed_url.path,
                "rawQueryString": parsed_url.query,
                "cookies": self._parse_cookies(),
                "headers": dict(self.headers),
                "queryStringParameters": query_string_params if query_string_params else None,
                "requestContext": {
                    "accountId": "123456789012",
                    "apiId": "test-api-id",
                    "authentication": None,
                    "authorizer": None,
                    "domainName": "localhost",
                    "domainPrefix": "localhost",
                    "http": {
                        "method": self.command,
                        "path": parsed_url.path,
                        "protocol": self.request_version,
                        "sourceIp": self.client_address[0],
                        "userAgent": self.headers.get("User-Agent", ""),
                    },
                    "requestId": str(uuid.uuid4()),
                    "routeKey": "$default",
                    "stage": "$default",
                    "time": time.strftime("%d/%b/%Y:%H:%M:%S +0000", time.gmtime()),
                    "timeEpoch": int(time.time() * 1000),
                },
                "body": body,
                "pathParameters": None,
                "isBase64Encoded": False,
                "stageVariables": None,
            }

            # Create context object
            context = type(
                "Context",
                (),
                {
                    "function_name": "test-function",
                    "function_version": "$LATEST",
                    "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:test-function",
                    "memory_limit_in_mb": "128",
                    "remaining_time_in_millis": lambda: 30000,
                    "log_group_name": "/aws/lambda/test-function",
                    "log_stream_name": "2023/01/01/[$LATEST]test",
                    "aws_request_id": str(uuid.uuid4()),
                },
            )()

            # Call handler function
            response = self.handler_func(event, context)

            # Handle different response formats
            if isinstance(response, dict):
                status_code = response.get("statusCode", 200)
                headers = response.get("headers", {})
                body = response.get("body", "")
                cookies = response.get("cookies", [])
                is_base64 = response.get("isBase64Encoded", False)
            else:
                # If handler returns non-dict, assume it's the body
                status_code = 200
                headers = {"Content-Type": "application/json"}
                body = json.dumps(response) if not isinstance(response, str) else response
                cookies = []
                is_base64 = False

            # Send HTTP response
            self.send_response(status_code)

            # Add CORS headers for localhost requests
            origin = self.headers.get("Origin", "")
            if "localhost" in origin or "127.0.0.1" in origin:
                self.send_header("Access-Control-Allow-Origin", origin)
            else:
                self.send_header("Access-Control-Allow-Origin", "http://localhost:*")

            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept, Origin")
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Access-Control-Max-Age", "86400")

            # Set headers
            for key, value in headers.items():
                self.send_header(key, value)

            # Set cookies
            for cookie in cookies:
                self.send_header("Set-Cookie", cookie)

            self.end_headers()

            # Send body
            if body:
                if is_base64:
                    import base64

                    body_bytes = base64.b64decode(body)
                else:
                    body_bytes = body.encode("utf-8")
                self.wfile.write(body_bytes)

        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
            raise e

    def _parse_cookies(self):
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return []
        return [cookie.strip() for cookie in cookie_header.split(";")]

    def log_message(self, format, *args):
        print(f"{self.address_string()} - - [{self.log_date_time_string()}] {format % args}")


def load_handler(handler_path):
    """Load handler function from module path"""
    try:
        if "." in handler_path:
            parts = handler_path.split(".")
            function_name = parts[-1]
            module_path = ".".join(parts[:-1])
        else:
            # Default to lambda_function.lambda_handler
            module_path = "lambda_function"
            function_name = "lambda_handler"

        module = import_module(module_path)
        handler_func = getattr(module, function_name)
        return handler_func
    except (ImportError, AttributeError) as e:
        print(f"Error loading handler {handler_path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP server for Lambda functions")
    parser.add_argument("--handler", default="lambda_function.lambda_handler", help="Handler function path (default: lambda_function.lambda_handler)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")

    args = parser.parse_args()

    # Load handler function
    handler_func = load_handler(args.handler)

    # Create handler class with the loaded function
    def handler_factory(*args, **kwargs):
        return LambdaHTTPHandler(handler_func, *args, **kwargs)

    # Start server
    server = HTTPServer((args.host, args.port), handler_factory)
    print(f"Starting server on {args.host}:{args.port}")
    print(f"Using handler: {args.handler}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
