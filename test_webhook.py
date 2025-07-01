import requests
import json
import argparse

def test_push_event(webhook_url):
    """Test a GitHub push event webhook"""
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'push'
    }
    
    payload = {
        "ref": "refs/heads/main",
        "after": "abc123def456",
        "sender": {
            "login": "Travis"
        }
    }
    
    print("Testing PUSH event...")
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
def test_pull_request_event(webhook_url):
    """Test a GitHub pull request event webhook"""
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'pull_request'
    }
    
    payload = {
        "action": "opened",
        "pull_request": {
            "id": "pr123",
            "head": {
                "ref": "staging"
            },
            "base": {
                "ref": "master"
            }
        },
        "sender": {
            "login": "Travis"
        }
    }
    
    print("\nTesting PULL_REQUEST event...")
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def test_merge_event(webhook_url):
    """Test a GitHub merge event webhook"""
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'pull_request_review'
    }
    
    payload = {
        "action": "submitted",
        "review": {
            "state": "approved"
        },
        "pull_request": {
            "id": "pr456",
            "head": {
                "ref": "dev"
            },
            "base": {
                "ref": "master"
            }
        },
        "sender": {
            "login": "Travis"
        }
    }
    
    print("\nTesting MERGE event...")
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test GitHub webhook events')
    parser.add_argument('--url', type=str, default='http://localhost:5000/webhook',
                        help='Webhook URL to test against')
    args = parser.parse_args()
    
    webhook_url = args.url
    
    test_push_event(webhook_url)
    test_pull_request_event(webhook_url)
    test_merge_event(webhook_url)
    
    print("\nAll tests completed!")
