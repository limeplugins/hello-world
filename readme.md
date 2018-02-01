# hello-world

_An example Lime CRM plugin_

This is an example plugin that implements:

* A custom endpoint that creates a deal, connects it to a company and a coworker, and creates a todo.
* An event handler that calls a configurable webhook upon receiving an event about the new deal.

## Running tests

On Linux:

```
$ make test
```

On Windows:

```
C:\src\hello-world> python -m venv venv
C:\src\hello-world> venv\Scripts\activate
C:\src\hello-world> python manage.py test
```

# Installation

```
$ limeplug install limeplugins/hello-world
```
