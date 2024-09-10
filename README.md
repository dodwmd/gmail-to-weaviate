# Gmail to Weaviate

This project fetches emails from a Gmail account, stores them in a Weaviate instance for easy searching and analysis, and provides a web interface for visualizing email insights.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Gmail API credentials
- Weaviate instance

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
   WEAVIATE_URL=http://localhost:8080
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Fetching Emails

To fetch emails and store them in Weaviate:

```
python gmail_to_weaviate.py
```

On the first run, the script will open a browser window for you to authenticate with your Google account. After authentication, it will automatically save the token to `token.json` for future use.

You can specify the maximum number of emails to process and the batch size:

```
python gmail_to_weaviate.py --max_emails 5000 --batch_size 200
```

### Web Interface

To run the web interface for email insights:

```
python app.py
```

This will start a Flask development server. Open a web browser and navigate to `http://localhost:5000` to view the email insights.

## Docker

To build and run the application using Docker:

1. Build the Docker image:
   ```
   docker build -t gmail-to-weaviate .
   ```

2. Run the Docker container:
   ```
   docker run -p 5000:5000 -e WEAVIATE_URL=http://host.docker.internal:8080 gmail-to-weaviate
   ```

   Note: Adjust the `WEAVIATE_URL` if your Weaviate instance is running elsewhere.

## Development

To start the development environment with hot reloading:

```
flask run --debug
```

## Testing

To run tests:

```
pytest tests/
```

## Linting

Lint the code with:

```
flake8 .
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.