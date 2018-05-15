from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Environment, select_autoescape, FileSystemLoader
import urllib.request
import json
import re


def display(element):
    """Called from a Jinja2 template to render recursively with bootstrap a given json"""
    if isinstance(element, dict):
        res = '<div class="card">'
        for i in element.keys():
            res += '<div class="card-body"><a style="font-weight: bold;">' + \
                str(i) + " : " + "</a>" + display(element[i]) + "</div>"
        res += "</div>"
    elif isinstance(element, list):
        res = '<div class="card"><ul class="card-body list-group list-group-flush">'
        for i in element:
            res += '<li class="list-group-item">' + display(i) + "</li>"
        res += "</ul></div>"
    else:
        res = str(element)
    return res


def loadContent(url):
    """ Load a content at the given url and return None if an error happen."""
    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        print('HTTPError: {}'.format(e.code))
        return None
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        print('URLError: {}'.format(e.reason))
        return None
    else:
        # Success
        return json.loads(conn.read())


def CommitListContent(contentList):
    """
    contentList should be a list of dictionnaries containing informations about the commits
    Return the important information about the given comits in the following shape :
        [   {   message : string,
                date : string,
                sha : string,
                login : string,
                avatar_url : string },
                ...
        ]
    Any missing value will be None.
    """
    importantContentList = []
    for content in contentList:
        # If committer or author not defined
        if content.get("committer") is None:
            if content.get("author") is None:
                login = "unknown"
                avatar_url = ""
                date = "unknown"
            else:
                login = content.get("author", {}).get("login")
                avatar_url = content.get("author", {}).get("avatar_url")
                date = content.setdefault("commit", {}).setdefault(
                    "author", {}).get("date")
                # Formating date
                date = date[:10]+" at "+date[11:-1]
        else:
            login = content.get("committer", {}).get("login")
            avatar_url = content.get("committer", {}).get("avatar_url")
            date = content.setdefault("commit", {}).setdefault(
                "committer", {}).get("date")
            # Formating date
            date = date[:10]+" at "+date[11:-1]

        # Shortening long commit messages
        message = content.setdefault("commit", {}).get("message")
        if len(message) > 70:
            message = message[:70]+" (...)"

        importantContentList.append({
            "message": message,
            "date": date,
            "sha": content.get("sha"),
            "login": login,
            "avatar_url": avatar_url
        })
    return importantContentList


def CommitContent(content):
    """content is a json of dictionnaries containing all informations about a commit.
    This function add to the content additional informations to help renderering the commit"""
    # Committer and author might carry or not the profile information.
    if not(content.get("committer") is None):
        content["profile_html_url"] = content.get(
            "committer").setdefault("html_url", "")
        content["profile_avatar_url"] = content.get(
            "committer").setdefault("avatar_url", "")
    elif not(content.get("author") is None):
        content["profile_html_url"] = content.get(
            "author").setdefault("html_url", "")
        content["profile_avatar_url"] = content.get(
            "author").setdefault("avatar_url", "")
    else:
        content["profile_html_url"] = ""
        content["profile_avatar_url"] = ""
    return content


# Setting up Jinja2 template environment
env = Environment(
    loader=FileSystemLoader('./templates')
)
# Global function callable from jinja's template
env.globals['display'] = display
# Templates
CommitListTemplate = env.get_template('commitList.html')
CommitTemplate = env.get_template('commit.html')
# Application parameters
PORT_NUMBER = 8000
url_repository = "https://api.github.com/repos/torvalds/linux/commits"


class myHandler(BaseHTTPRequestHandler):
    """Overwritting the BaseHTTPRequestHandler to implement GET requests """

    def do_GET(self):
        # Matching the URL with the requested routes
        m = re.match(r"^(\/\w+)?\/?$", self.path)
        if not(m is None):
            if m.group(1) is None:
                # The user query the list of commits
                contents = loadContent(url_repository)
                if isinstance(contents, list):
                    contents = CommitListContent(contents)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(CommitListTemplate.render(
                        contents=contents).encode())
                else:
                    self.send_error(
                        500, "Unexpected content format from the API")
            else:
                # The user query a given commit
                content = loadContent(url_repository+m.group(1))
                if not(content is None) and isinstance(content, dict) and not(content.get("message") == "Not Found"):
                    content = CommitContent(content)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(
                        CommitTemplate.render(content=content).encode())
                elif content.get("message") == "Not Found":
                    self.send_error(
                        404, "Commit Not Found {}".format(self.path))
                else:
                    self.send_error(
                        500, "Unexpected content format from the API")
        else:
            self.send_error(404, "Commit Not Found {}".format(self.path))
        return


try:
    # Create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ', PORT_NUMBER)
    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    # If the server is interupted
    print('^C received, shutting down the web server')
    server.socket.close()
