```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
GITHUB_TOKEN="your token" python
>>> import githubrelease
>>> gh = githubrelease.Github(repo='your/repository')
>>> gh.release('Release title') # creates new tag and release
```
