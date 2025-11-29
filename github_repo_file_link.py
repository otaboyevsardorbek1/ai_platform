import requests

def get_github_files(owner, repo, path=""):
    """
    GitHub REST API yordamida barcha fayllarni olish
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Xatolik: {response.status_code}")
        return []
    
    items = response.json()
    file_links = []

    for item in items:
        if item['type'] == 'file':
            file_links.append(item['html_url'])
        elif item['type'] == 'dir':
            # Papkani rekursiv tekshirish
            file_links.extend(get_github_files(owner, repo, item['path']))
    
    return file_links

if __name__ == "__main__":
    repo_url = input("GitHub repository URL ni kiriting: ").strip()
    # URL dan owner va repo nomini ajratish
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    links = get_github_files(owner, repo)
    
    print("\nTopilgan barcha fayl linklari:\n")
    for link in links:
        print(link)
    
    print(f"\nJami {len(links)} ta fayl topildi.")
    with open("github_file_links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")