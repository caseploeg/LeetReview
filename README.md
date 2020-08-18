# LeetReview

A code review tool that scrambles correct code solutions to LeetCode questions and asks you to recreate the original.
Made to help develop pattern recognition in algorithms and practice "leetcoding" without a keyboard.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the 
project on a live system.

### Prerequisites

Python3, Pip and Python3-venv, instructions are written assuming use of a linux-based system

### Installing

Create and activate a virtual environment at the base of the project

```
$ python3 -m venv venv
$ . venv/bin/activate
```

Install Flask and set up environment variables

```
$ pip install Flask
$ export FLASK_APP=leetreview
$ export FLASK_ENV=development
```

Initialize the database and run the development server
```
$ flask init-db
$ flask run
```

## Deployment

https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
