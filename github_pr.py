import requests
from datetime import datetime, timedelta
import statistics

base_url = "https://api.github.com"
repo_owner = "your_repo_owner"
repo_name = "your_repo_name"
token = "your_token"


headers = {
    "Authorization": f"token {token}",
    "Accept": "application/json"
}

def fetch_prs(page):
    url = f"{base_url}/repos/{repo_owner}/{repo_name}/pulls"
    params = {"state": "closed", "per_page": 5, "page": page}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching PRs: {response.status_code}")
        print(response.text)
        return []
    return response.json()

def fetch_pr_reviews(pr_number):
    url = f"{base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching reviews for PR {pr_number}: {response.status_code}")
        print(response.text)
        return []
    return response.json()

def calculate_time_difference(created_at, approved_at):
    created_time = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    approved_time = datetime.strptime(approved_at, "%Y-%m-%dT%H:%M:%SZ")
    return approved_time - created_time

def format_timedelta(td):
    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days} days {hours} hours {minutes} minutes {seconds} seconds"

def average_timedelta(deltas):
    if not deltas:
        return None
    total_seconds = sum(delta.total_seconds() for delta in deltas)
    return timedelta(seconds=total_seconds / len(deltas))

prs = []
for page in range(1, 2):
    page_prs = fetch_prs(page)
    if not page_prs:
        break
    prs.extend(page_prs)

print(f"Retrieved {len(prs)} PRs")

first_approved_diffs = []
valid_prs = []

for pr in prs:
    try:
        pr_number = pr["number"]
        created_at = pr["created_at"]
    except KeyError as e:
        print(f"Error accessing PR data: {e}")
        print(f"PR data: {json.dumps(pr, indent=2)}")
        continue

    reviews = fetch_pr_reviews(pr_number)
    
    approved_reviews = [review for review in reviews if review.get("state") == "APPROVED"]
    approved_reviews.sort(key=lambda x: x["submitted_at"])
    
    if len(approved_reviews) >= 1:
        first_diff = calculate_time_difference(created_at, approved_reviews[0]["submitted_at"])
        
        print(f"PR #{pr['number']}:")
        print(f"  First approved time difference: {format_timedelta(first_diff)}")

        valid_prs.append({
            "number": pr_number,
            "first_diff": first_diff
        })
        
        first_approved_diffs.append(first_diff)

first_avg = average_timedelta(first_approved_diffs)

print(f"\nTotal PRs with at least one approval: {len(valid_prs)}")
print("\nAverage time differences:")
print(f"  First approval: {format_timedelta(first_avg)}" if first_avg else "  No first approvals")
print("main")
