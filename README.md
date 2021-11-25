# REST API for a messaging app with Python

## Introduction

This is an in-memory solution for implementing a simple backend for a messaging sharing service.
The solution uses an in-memory database service, Redis.
The API is built with Python and uses the Flask library, and is not suitable at the moment for a production environment.

## Installation

There are three ways of building this application

### On a local machine

#### Requirements:

- Python 3.8 or later
- A [Redis installation](https://redis.io/topics/quickstart)

#### Installation:

Create a virtual environment and install the requirements with pip3

```console
foo@bar:messaging_api$ python3 -m venv virtualenv
[...]
foo@bar:messaging_api$ pip3 install -r requirements.txt
```

Export environment variables for Flask (replace `development` with `production` for production environment)

```console
foo@bar:messaging_api$ export FLASK_APP=app/messaging_api.py
foo@bar:messaging_api$ export FLASK_ENV=development
```

Run the application

```console
foo@bar:messaging_api$ flask run
[...]
```

### With Docker from source

#### Requirements

- A Docker installation with `docker-compose`

Run the following command to build the docker images for the API and Redis and launch their associated container in detached mode:

```console
foo@bar:messaging_api$ docker-compose -f docker-compose.dev.yml up -d
```

## Running tests

Launch the Flask and Redis server and run the following command
```console
foo@bar:messaging_api$ pytest tests/test_pytest.py
```

## Security risks and considerations regarding the API

The principal security assumptions for the project are the following:

- The service provided by the API is public. Anyone with a valid URL to a message should be able to access this message

- Guessing message identifiers should not be feasible

### Architecture and workflow of the API

The API serves only over 2 URLs:

- `/` : The root address. This page accepts both `GET` and `POST` methods HTTP requests.
- `/msg/<message_id>` : The set of addresses from which posted messages can be accessed. This set of address only accepts `GET` method HTTP request. 

The permitted methods are implemented using an allow list. All requests not matching the allow list are rejected with HTTP response code `405 Method not allowed`.

Each response also includes security headers [recommended by OWASP](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html). 

### UUID against message ID guessing

In order to make message identifiers infeasible to guess, they are generated using an UUID4 method, which generates a random UUID string. Such a string has 2^38 possible combinations, which makes possible collisions very unlikely. I have chosen this UUID method since UUID1 includes data about the computer, which is unwanted.

### Logging

Logs are one of the limits of the in-memory solution, since they are text files stored on disk. However, I strongly believe that thorough logging is part of the good practices of secure development.

Since docker containers are stateless, logs won't be persistent in case of the container being stopped or crashing. To remediate that, I have used a volume to store logs. They can be found at `/var/log/messaging_api`.

The logging strategy for the application is to use a log file called `messaging_api.log` that stores logs. Each day at midnight, this log file is stored as `messaging_api.log.yymmdd`. Having a logging storage strategy is important, since organizations take 200 on average to identify breaches.

### SQL and NoSQL injections

Redis is immune from escaping issues, as stated in its [documentation](https://redis.io/topics/security):
> The Redis protocol has no concept of string escaping, so injection is impossible under normal circumstances using a normal client library. The protocol uses prefixed-length strings and is completely binary safe.

## Security considerations that are still a work in progress

### TLS support

The main concern on the confidentiality side is the absence of TLS encryption for the HTTP request to and from the API. At moment of writing, I have had the choice to either enable encryption using built-in SSL encryption keys that would have ended up in the docker image, or to use a script to generate a self-signed certificate at run time. I had a lot of trouble implementing the first solution, and I am still investingating it at moment of writing, since the second option does not seem to be desirable in a production environment.

### Rate limitation to prevent Denial of Service

One of the main risks on the availability side of the API is that there is, at moment of writing, no implementation of a rate-limiting feature that would prevent an actor from sending hundreds of concurential requests to the API service and potentially making it unavailable. The rate-limiting feature can be added using the `flask_limiter` library.

While Redis is built with speed and high-availability in mind, Flask may become unstable, especially under the production configuration in place right now. In the current in-memory configuration, Redis has no way of keeping data if th container had to stop. But since we can estimate that it Flask would stop before Redis, it might be safe to consider it would likely not be affected.

## Security risks and assumptions regarding the Docker containers

### Running the container as an unpriviledged user

Root in a container is the same root as on the host machine, but restricted by the docker daemon configuration. No matter the limitations, if an actor breaks out of the container, he will still be able to find a way to get full access to the host. The threat model can't ignore the risk posed by running as root. As such, it is best to specify a user and to run the container as an unpriviledged user. The flask application runs with the `messaging_api` user.

### Application networking in docker

The application is not designed to provide network segmentation when running from source on a local machine, or when running the docker images built from the `docker-compose.dev.yml` file.

However, running the images from the `docker-compose.yml` file provides isolation from the Internet for Redis. This layer of segmentation has been implemented using an internal bridge network that is both used by Redis and the Flask API while only Flask has access to the Internet by using the external bridge connection.

This should prevent unauthorized direct access to the database from unauthorized actors.

#### Graph of the network layout in production 

```
          +-----------+                    +---------+
          |           |                    |         |
          | FLASK API |---              ---|  Redis  |
          |           |  |              |  |         |
          +-----------+  |              |  +---------+
             |           |              |  
+------------------+   +------------------+           
| frontend bridge  |   |  backend bridge  |
|     network      |   |      network     |
+------------------+   +------------------+
          |
       Internet
```
## Other security protections considerations

### Web Application Firewalls

Another good solution to protect the API service from a Denial of Service attack or eventual injection attacks would be to use a `Web Application Firewall (WAF)`. They work similarly to network firewalls, but on the Application layer. A WAF sits in front of a web server and receives all network traffic headed to that server. It then scrutinizes the input headed to that application, performing input validation before passing it to the web server. This prevents malicious traffic from ever reaching the web server and acts as an importnt component of a layered defense against web application vulnerabilities.
