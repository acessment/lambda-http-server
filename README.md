# lambda-http-server

A simple HTTP server that converts requests to Lambda function event objects and returns HTTP responses according to the function's return value, which roughly means you can test Lambda function URLs locally.

It simulates AWS Lambda function URL behavior. This package allows you to run a local server that can handle HTTP requests and invoke a specified handler function, mimicking the AWS Lambda environment.

## Disclaimer and Limitations

The package is vibe coded and not fully tested. In our use case, our Lambda function serves as a simple function URL with no additional integration with other AWS services. If your Lambda function relies on other AWS services or has complex dependencies, this package may not fully replicate the AWS ecosystem and you are advised to check out the official documentation for testing Lambda functions locally.

## Installation

To install the package, you can use pip:

```
pip install git+https://github.com/acessment/lambda-http-server.git
```

## Usage

To run the server, use the following command in your project directory:

```
python -m lambda_http_server --handler <your_handler> --port <port_number>
```

Replace `<your_handler>` with the path to your handler function (e.g., `my_module.my_handler`, default is `lambda_function.lambda_handler`) and `<port_number>` with the desired port number (default is 8000).

### Example

If you have a handler function defined in `my_module.py` as `my_handler`, you can start the server with:

```
python -m lambda_http_server --handler my_module.my_handler --port 8000
```

## Configuration

You can specify additional options such as the host:

```
python -m lambda_http_server --handler my_module.my_handler --port 8000 --host localhost
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
