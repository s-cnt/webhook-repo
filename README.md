# GitHub Webhook Receiver

This is a Flask application that serves as a webhook endpoint for GitHub events. It receives webhook events from GitHub, stores them in MongoDB, and displays them in a UI.

## Features

- Webhook endpoint to receive GitHub events (Push, Pull Request, Merge)
- MongoDB integration to store event data
- UI that polls MongoDB every 15 seconds and displays the latest events

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd webhook-repo
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following content:
   ```
   MONGO_URI=mongodb://localhost:27017/github_events
   PORT=5000
   ```
   Adjust the MongoDB URI as needed.

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`.

5. **Configure Your GitHub Repository**:
   - Go to your GitHub repository settings
   - Add a webhook pointing to your webhook endpoint (e.g., `http://your-server:5000/webhook`)
   - Set the content type to `application/json`
   - Select the events you want to receive (push, pull_request)

## MongoDB Schema

The application uses the following MongoDB schema for storing GitHub events:

| Field       | Datatype        | Details                             |
|-------------|-----------------|-------------------------------------|
| _id         | ObjectID        | MongoDB default ID                  |
| request_id  | string          | Git commit hash or PR ID            |
| author      | string          | Name of GitHub user making the action |
| action      | string          | GitHub action type (PUSH, PULL_REQUEST, MERGE) |
| from_branch | string          | Source branch (for PR and merge)    |
| to_branch   | string          | Target branch                       |
| timestamp   | string(datetime)| UTC timestamp of the action         |

## API Endpoints

- `GET /`: UI for viewing GitHub events
- `POST /webhook`: Endpoint for receiving GitHub webhook events
- `GET /api/events`: API endpoint that returns the latest events from MongoDB
