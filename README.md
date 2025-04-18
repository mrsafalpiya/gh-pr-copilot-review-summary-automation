# GitHub Copilot PR Automation

This tool automates the process of requesting GitHub Copilot reviews and generating Copilot summary comments for Pull Requests. It's designed to work with a RabbitMQ message queue to process PR review requests asynchronously.

## Features

- Automatically request/re-request GitHub Copilot reviews for PRs
- Generate GitHub Copilot summary comments for PR changes
- Support for both new PRs and synchronized (updated) PRs
- Queue-based processing with RabbitMQ for reliability

## Prerequisites

- Python 3.8+
- Firefox browser
- RabbitMQ server
- GitHub account with access to GitHub Copilot

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/github-copilot-pr-automation.git
cd github-copilot-pr-automation
```

### 2. Install Dependencies

```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
pip install -r requirements.txt
```

### 3. Download GeckoDriver

Download the latest [geckodriver](https://github.com/mozilla/geckodriver/releases) for your system and place it in the project directory.

```bash
# Make it executable
chmod +x geckodriver
```

### 4. Create Firefox Profile for GitHub Login

1. Run Firefox with the profile manager:
   ```bash
   firefox -P
   ```
2. Create a new profile named "For Automation" (or any name you prefer)
3. Launch Firefox with this profile and log in to GitHub
4. Find your profile directory by navigating to `about:profiles` in Firefox
5. Note the "Root Directory" path of your profile

### 5. Configure Environment Variables

Copy the provided `.env.example` file to create your own `.env` file:

```bash
cp .env.example .env
```

Then edit the `.env` file and update the values with your own configuration:

```
# RabbitMQ
RABBITMQ_USER="your_rabbitmq_username"
RABBITMQ_PASS="your_rabbitmq_password"
RABBITMQ_HOST="localhost"  # Optional, defaults to localhost
RABBITMQ_PORT=5672         # Optional, defaults to 5672

# Selenium
FIREFOX_PROFILE_PATH="~/.mozilla/firefox/your_profile_id.For Automation"
FIREFOX_BINARY_PATH="/usr/bin/firefox"  # Adjust for your system if needed
GECKODRIVER_PATH="./geckodriver"
```

Replace the placeholder values with your actual settings:
- `RABBITMQ_USER` and `RABBITMQ_PASS` with your RabbitMQ credentials
- `FIREFOX_PROFILE_PATH` with the profile path you noted in step 4
- `FIREFOX_BINARY_PATH` with the path to Firefox on your system

## Running the Service

```bash
python main.py
```

The service will start and listen for messages on the RabbitMQ queue named `gh-pr-copilot-review-summary`.

## Message Format

The service expects messages in the following JSON format:

```json
{
  "type": "opened",  // or "synchronized" for updated PRs
  "pr_link": "https://github.com/org/repo/pull/123"
}
```

- `type`: Either "opened" for new PRs or "synchronized" for updated PRs
- `pr_link`: The full URL to the GitHub pull request

## Troubleshooting

- **Selenium Issues**: Make sure Firefox and geckodriver versions are compatible
- **Authentication Issues**: Verify that the Firefox profile has an active GitHub login session
- **RabbitMQ Connection**: Check RabbitMQ credentials and server availability

## License

[MIT](LICENSE)