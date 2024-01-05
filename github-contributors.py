import requests

repo = "kylecorry31/Trail-Sense"

url = f"https://api.github.com/repos/{repo}/contributors?q=contributions&order=desc&per_page=100"

def get_all_contributors():
    page = 1
    contributors = []
    while True:
        response = requests.get(url + f"&page={page}")
        page_contributors = response.json()
        if len(page_contributors) == 0:
            break
        contributors.extend(page_contributors)
        page += 1
    return contributors

contributors = get_all_contributors()

usernames = [contributor["login"] for contributor in contributors]

print('\n'.join(usernames))