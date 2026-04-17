import urllib.request
import os

skills = {
    "install-errands": "https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/skills/install-errands/SKILL.md",
    "use-instawork": "https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/skills/use-instawork/SKILL.md",
}

for skill, url in skills.items():
    path = os.path.expanduser(os.path.join("~", ".cursor", "skills", skill))
    os.makedirs(path, exist_ok=True)
    urllib.request.urlretrieve(url, os.path.join(path, "SKILL.md"))
    print("Installed " + skill)
