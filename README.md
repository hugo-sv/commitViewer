# Commit Viewer 

This project is a native python 3.6 web application displaying a list of commits from a repository and details on any specific commits.

The repository URL is ```https://github.com/torvalds/linux```

## Installation

To run the server, you need the following packages :
- http
- jinja2
- urllib
- json
- re

You can install them with the following command :

```pip install http jinja2 urllib json re```

You can go in the project folder and run :

```python commitViewer.py```

The server will be listening on port 8000.

## Architecture

The Project contains this README and three files :
- commitViewer.py is the python server file
- templates/commit.html and templates/commitList.html are the template HTML files corresponding to different app views.

Two routes are provided :
- / :  The main page, display the list of the commit from the Repository.
- /[Commit's hash] : This route display the requested commit from it Hash.

## Approach

To realise this project, I first implemented the back-end functions.
With the ```http``` python module, I created a basic HTTP Request Handler for which I implemented a GET route.
I then interpreted the requested URL with Regex, and the ```re``` python module, in order to return the requested information when a user ask for a commit details.
To retrieve the informations from the API, I used the ```urllib``` module which allow making basic request.
I then converted the content from the request into a readeable object with the ```json``` module.

Next, I started to implement the front rendering by choosing ```jinja2``` as a rendering engine to rendre HTML CSS pages with parameters.
I then developped the two templates and tested basic view of the requested json.

Willing to implement a great design, I tried to use Semantic UI for front-end, but I did not manage to make it work well with Jinja and python, so I decided to use Bootstrap imported from URL in the HTML template files.

Another difficulty I met was to handle the cases where an author or a comitter, or both wasn't defined.
 

## Improvements

If I could spend more time on this project, I would work on the user interface in order to implement :
 - A navigation bar on the list of commits views in order to filter or search commits.
 - Dropables menus in the commit details, in order to improve the navigation process within all the data.

 I would also have tried to implement the front end with react, in order to produce a more dynamic front end. And make some implementation easier.