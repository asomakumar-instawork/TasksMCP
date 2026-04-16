import urllib.request
import os

base = "https://raw.githubusercontent.com/asomakumar-instawork/TasksMCP/main/.cursor/skills"
skills = ["install-tasksmcp", "use-instawork"]

for skill in skills:
    path = os.path.expanduser(os.path.join("~", ".cursor", "skills", skill))
    os.makedirs(path, exist_ok=True)
    urllib.request.urlretrieve(base + "/" + skill + "/SKILL.md", os.path.join(path, "SKILL.md"))
    print("Installed " + skill)
