import argparse
import os
import re

from github3 import login


DIGITS = re.compile(r'(\d+)')

def suggest_next_version(latest_tag_name):
    '''increments minor version
    
    >>> suggest_next_version('1')
    '1.0.1'
    
    >>> suggest_next_version('1.2.3')
    '1.2.4'
    
    >>> suggest_next_version('v1.2.3-4')
    'v1.2.4'
    '''
    parsed = [int(num,10) for num in DIGITS.findall(latest_tag_name)]
    length = len(parsed)

    # ensure three numbers
    if length < 3:
        parsed.extend([0]*(3-length))

    # increment minor version
    parsed[2] = parsed[2] + 1

    prefix = 'v' if latest_tag_name.startswith('v') else ''
    return prefix + '.'.join(str(num) for num in parsed[:3]) 


class Github:
    def __init__(self, token=None, repo=None):
        self.token = token
        self.gh = None
        self.repo = None

        if token is None:
            self.init_from_envvar()
        self.gh = login(token=self.token)
        self.set_repo(repo)


    def set_repo(self, repo=''):
        self.repo = self.gh.repository(*repo.split('/')) if repo else None


    def init_from_envvar(self):
        self.token = os.environ['GITHUB_TOKEN']

    
    def latest_release(self):
        return next(self.repo.releases(1), None)

    
    def next_tag_name(self, latest_tag_name=None):
        if not latest_tag_name:
            release = self.latest_release()
            latest_tag_name = release.tag_name
        return suggest_next_version(latest_tag_name)

    def release(self, title, tag_name=None, latest_release=None):
        if tag_name is None:
            if latest_release is None:
                latest_release = self.latest_release()
            if latest_release is None:
                raise Exception('Need tag_name')
            tag_name = suggest_next_version(latest_release.tag_name)

        description = '# ' + '\n\n# '.join(commit.message for commit in self.repo.compare_commits(latest_release.tag_name, 'master').commits)
        html_compare_url = self.repo.html_url + '/compare/' + latest_release.tag_name + '...' + tag_name
        body = html_compare_url + '\n\n' + description
        return self.repo.create_release(tag_name, name=title, body=body)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo')
    args = parser.parse_args()


