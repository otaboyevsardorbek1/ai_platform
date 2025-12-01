import requests

def get_github_folders(owner, repo):
    """
    GitHub REST API yordamida repo ichidagi barcha papkalarni olish.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Xatolik: {response.status_code}")
        return []

    items = response.json()
    dirs = []
    
    for item in items:
        if item['type'] == 'dir':  # faqat papkalarni olish
            dirs.append(item['name'])
    
    return dirs

def get_github_files(owner, repo, path=""):
    """
    GitHub REST API yordamida ixtiyoriy pathdagi fayllarni olish.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Xatolik: {response.status_code}")
        return []

    items = response.json()
    file_links = []
    
    for item in items:
        if item['type'] == 'file':  # Faylni aniqlash
            file_links.append(item['html_url'])
        elif item['type'] == 'dir':  # Agar papka bo'lsa, uni rekursiv tekshirish
            file_links.extend(get_github_files(owner, repo, item['path']))
    
    return file_links

if __name__ == "__main__":
    repo_url = input("GitHub repository URL ni kiriting: ").strip()
    # URL dan owner va repo nomini ajratish
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    
    # Repodagi barcha papkalarni olish
    dirs = get_github_folders(owner, repo)
    
    if not dirs:
        print("Repo ichida papkalar topilmadi.")
        exit()

    # Papkalar ro'yxatini foydalanuvchiga ko'rsatish va tanlashni so'rash
    print("\nRepo ichidagi papkalar:")
    for i, dir_name in enumerate(dirs, 1):
        print(f"{i}. {dir_name}")
    
    # Foydalanuvchidan qaysi papkada ishlashni tanlash
    folder_choice = int(input("\nQaysi papkada fayllarni olishni xohlaysiz? (raqamini kiriting): ")) - 1
    if folder_choice < 0 or folder_choice >= len(dirs):
        print("Noto'g'ri tanlov.")
        exit()
    
    selected_folder = dirs[folder_choice]
    print(f"\nTanlangan papka: {selected_folder}")

    # Tanlangan papkadagi fayllarni olish
    links = get_github_files(owner, repo, path=selected_folder)
    
    if not links:
        print("Tanlangan papkada fayllar topilmadi.")
        exit()

    # Fayl URL'larini chiqarish
    print("\nTopilgan fayl linklari:\n")
    for link in links:
        print(link)
    
    print(f"\nJami {len(links)} ta fayl topildi.")
    
    # Fayl linklarini faylga yozish
    with open("github_file_links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")
