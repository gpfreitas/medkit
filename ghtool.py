import json
import sys
import os
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth


def api_get(endpoint, params=None):
    """Call Github api.

    verb: GET, POST, etc.
    endpoint: the relative path, like '/user'
    params: map to pass into the `params` keyword of requests.get

    Your Github credentials should be stored in an environment variable 'GH' in
    a string 'user,token', so user and token seperated by a comma.

    See the GitHub API docs for functionality.
    """
    api_root = 'https://api.github.com'
    url = urljoin(api_root, endpoint)
    user, token = os.environ['GH'].split(',')
    r = requests.get(url, auth=(user, token), params=params)
    return r



if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        print("Args: ", args)
        raise ValueError("Script only takes one input parameter, the GitHub API endpoint")
    endpoint = args[0]
    r = api_get(endpoint)
    print(r.content.decode(encoding='utf-8'))

