# Gmail to Weaviate

This project fetches emails from a Gmail account and stores them in a Weaviate instance for easy searching and analysis.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Gmail API credentials

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gmail-to-weaviate.git
   cd gmail-to-weaviate
   ```

2. Set up Gmail API credentials:
   a. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   b. Create a new project or select an existing one.
   c. Enable the Gmail API for your project.
   d. Create OAuth 2.0 credentials (select "Desktop app" as the application type).
   e. Download the credentials JSON file and save it as `credentials.json` in the project root.

3. Create a `.env` file in the project root and add your Weaviate configuration:
   ```
   WEAVIATE_URL=http://weaviate:8080
   LOG_LEVEL=INFO
   ```

4. Install dependencies:
   ```
   make setup
   ```

## Usage

To run the application:

```
python gmail_to_weaviate.py
```

On the first run, the script will open a browser window for you to authenticate with your Google account. After authentication, it will automatically save the token to `token.json` for future use.

You can specify the maximum number of emails to process and the batch size:

```
python gmail_to_weaviate.py --max_emails 5000 --batch_size 200
```

## Development

To start the development environment with hot reloading:

```
tilt up
```

## Testing

Run tests with:

```
make test
```

## Linting

Lint the code with:

```
make lint
```

## Building

Build the Docker image with:

```
make build
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
