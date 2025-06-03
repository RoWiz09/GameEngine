import requests

# This script fetches all releases of a specified GitHub repository and allows the user to download a selected release as a zip file.
owner = "RoWiz09"
repo = "Autoflipper"  # Ensure this repository exists and is public
def get_all_releases(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    response = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"})  # Use GitHub API headers

    # Check if the request was successful
    if response.status_code == 404:
        print(f"Repository '{repo_owner}/{repo_name}' not found.")
        return None
    elif response.status_code != 200:
        print(f"Failed to fetch releases. Status code: {response.status_code}")
        return None
    else:
        return response.json()

all_releases = get_all_releases(owner, repo)

if all_releases:
    print("Available releases:")
    for idx, release in enumerate(all_releases):
        print(f"{idx + 1}: {release['name']}")

    try:
        choice = int(input("Enter the number of the release you want to download: ")) - 1
        if 0 <= choice < len(all_releases):
            selected_release = all_releases[choice]
            download_url = selected_release['zipball_url']
            file_name = f"{repo}-{selected_release['name']}.zip"

            print(f"Downloading source code as {file_name} from {download_url}...")
            
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                with open(file_name, 'wb') as file:
                    file.write(download_response.content)
                
                print(f"Downloaded {file_name} successfully.")
            else:
                print(f"Failed to download {file_name}. Status code: {download_response.status_code}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")
else:
    print("Could not retrieve releases.")