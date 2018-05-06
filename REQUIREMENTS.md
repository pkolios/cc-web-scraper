# Fullstack coding challenge: A simple Web-Application for Analyzing Web-Sites

The objective is to build a web-application that does some analysis of a web-page/URL.


## Functional Requirements

* The application should show a form with a text-field thus the user can type in the URL of the webpage being analyzed.

* Additionally, the form should contain a button for sending the input to the server as well as to trigger the server-side analysis process.

* After processing the results should be shown to the user in terms of a simple table below to the form. The result comprises the following information:

** What HTML version has the document?

** What is the page title?

** How many headings of what level are in the document?

** How many internal and external links are in the document? Are there any inaccessible links and how many?

** Did the page contain a login-form?


In case the URL given by the user is not reachable an error message should appear below the input form. The message should contain the HTTP status-code and some useful error description.


## Non-Functional Requirements:

The backend should cache the scraping results for each URL for 24 hours such that your backend does not have to redo the scraping for any given URL within the next 24 hours.
Your application server as well as your data store should be run in separate Docker containers such that they can later on be scaled independently.

## Your Solution

Please write an application handling all the wanted features. HINT: for document analysis consider using a library.

For the frontend part, please use Angular (version 5 preferred) or React. Additionally, you can use all the available libraries and frameworks available on the internet.
For the backend part, feel free to use a technology stack of your preference.


## Submission of Results

Please provide the result as a Git repository with this content:

1. The project with all source files.

2.  A docker-compose setup to run the backend.

3. A short text document that lists the main steps of building your solution as well as all assumptions/decisions you made in case of unclear requirements or missing information

