import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/github_events")
mongo = PyMongo(app)

# Add some sample events for testing
def add_sample_events():
    # Clear existing events
    mongo.db.events.delete_many({})
    
    # Add sample PUSH event
    push_event = {
        "request_id": "abc123",
        "author": "Travis",
        "action": "PUSH",
        "to_branch": "staging",
        "timestamp": "2021-04-01T21:30:00Z"
    }
    
    # Add sample PULL_REQUEST event
    pr_event = {
        "request_id": "pr456",
        "author": "Travis",
        "action": "PULL_REQUEST",
        "from_branch": "staging",
        "to_branch": "master",
        "timestamp": "2021-04-01T09:00:00Z"
    }
    
    # Add sample MERGE event
    merge_event = {
        "request_id": "merge789",
        "author": "Travis",
        "action": "MERGE",
        "from_branch": "dev",
        "to_branch": "master",
        "timestamp": "2021-04-02T12:00:00Z"
    }
    
    # Insert events
    mongo.db.events.insert_many([push_event, pr_event, merge_event])
    print("Sample events added to MongoDB")

# Add sample events when app starts
with app.app_context():
    add_sample_events()

@app.route('/')
def index():
    """Render the main UI page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint to receive GitHub webhook events"""
    if request.headers.get('X-GitHub-Event'):
        payload = request.json
        
        # Extract relevant information based on the event type
        event_type = request.headers.get('X-GitHub-Event')
        
        # Initialize data dictionary for MongoDB
        data = {
            "request_id": payload.get('after') or payload.get('pull_request', {}).get('id'),
            "author": payload.get('sender', {}).get('login'),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "action": None,
            "from_branch": None,
            "to_branch": None
        }
        
        # Handle different event types
        if event_type == "push":
            data["action"] = "PUSH"
            data["to_branch"] = payload.get('ref', '').replace('refs/heads/', '')
            
        elif event_type == "pull_request":
            data["action"] = "PULL_REQUEST"
            pr = payload.get('pull_request', {})
            data["from_branch"] = pr.get('head', {}).get('ref')
            data["to_branch"] = pr.get('base', {}).get('ref')
            
        elif event_type == "pull_request_review" and payload.get('action') == "submitted":
            if payload.get('review', {}).get('state') == "approved":
                data["action"] = "MERGE"
                pr = payload.get('pull_request', {})
                data["from_branch"] = pr.get('head', {}).get('ref')
                data["to_branch"] = pr.get('base', {}).get('ref')
        
        # Store data in MongoDB if action is recognized
        if data["action"]:
            mongo.db.events.insert_one(data)
            return jsonify({"status": "success", "message": f"{data['action']} event recorded"}), 201
    
    # Return 400 Bad Request if the event couldn't be processed
    return jsonify({"status": "error", "message": "Could not process webhook event"}), 400

@app.route('/api/events', methods=['GET'])
def get_events():
    """API endpoint to retrieve the latest events from MongoDB"""
    # Get the latest events, sorted by timestamp in descending order
    latest_events = list(mongo.db.events.find(
        {}, 
        {'_id': 0}
    ).sort("timestamp", -1).limit(10))
    
    return jsonify(latest_events)

@app.route('/api/events')
def get_all_events():
    """Return all events from MongoDB as JSON"""
    # Query the most recent events, limited to 100
    events_cursor = mongo.db.events.find({}).sort('timestamp', -1).limit(100)
    
    # Convert ObjectId to string for JSON serialization
    events = []
    for event in events_cursor:
        event['_id'] = str(event['_id'])
        events.append(event)
    
    return jsonify(events)

@app.route('/admin')
def admin_view():
    """Admin interface to view all MongoDB events"""
    try:
        # Query all events
        events_cursor = mongo.db.events.find({}).sort('timestamp', -1)
        
        # Convert events for template rendering
        events = []
        for event in events_cursor:
            event['_id'] = str(event['_id'])
            events.append(event)
        
        # Return simple HTML display
        return render_template('admin.html', events=events, db_status="Connected to MongoDB")
    except Exception as e:
        return render_template('admin.html', events=[], db_status=f"Error: {str(e)}")

@app.route('/api/all-events')
def all_events():
    """Return all events from MongoDB as raw JSON (for debugging)"""
    try:
        events_cursor = mongo.db.events.find({}, {'_id': 0})
        events = list(events_cursor)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='localhost', port=int(os.getenv("PORT", 5000)), debug=True)
