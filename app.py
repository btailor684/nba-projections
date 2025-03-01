import requests

API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# Test the API call
url = f"{BASE_URL}/stats?player_ids[]=117&per_page=10&sort=game.date&order=desc"
response = requests.get(url, headers=HEADERS)

print(response.status_code)
print(response.json())  # This will show any errors
