# Docker-Setup.py
Create Docker Containers from simple templates

## Why?
Everytime I need a database in my projects, I need to create a new docker container and for that, 
lookup all the config values that are needed for this specific database. With this script, you can set up
the template for a specific database container once and instantiate them later, without having to remember
all the environment variables and volume mountpoints.

## How does it work?
Every template has arguments that are prompted at the beginning.
These can have default values and a description to show to the user.

After that these arguments are inserted into volume names, environment variables, the container name,
ports and the defaults of other arguments.
All these values are merged into a single `docker run` command and
needed volumes are created automatically.

This makes the building of the `docker run` command an interactive process.

## How to use?
To start the script, run `python3 docker-setup.py <template-name>` the script will guide you through
the container creation.

## Config format
The config file is in JSON format and every container template corresponds to a key of the root object.
A template looks like this:
```json
{
  "arguments": {
    "name": "container name",
    "root_username": {
      "description": "root username",
      "default": "root"
    },
    "root_password": {
      "description": "root password",
      "default": "pw"
    },
    "port": {
      "default": "27017"
    },
    "database_name": {
      "description": "database name",
      "default": "{name}"
    }
  },
  "image": "mongo",
  "name": "{name}-mongo",
  "volumes": {
    "{name}-volume": "/data/db"
  },
  "ports": {
    "{port}": "27017"
  },
  "environment": {
    "MONGO_INITDB_ROOT_USERNAME": "{root_username}",
    "MONGO_INITDB_ROOT_PASSWORD": "{root_password}",
    "MONGO_INITDB_DATABASE": "{database_name}"
  }
}
```

* `arguments` is an object. Every key corresponds to the placeholder for the argument value.
The value can be either a string which acts as the description for the argument, or an object when
you want to set a default value. Previous arguments can be used in the default value of an argument.  
* `image` is the docker image for the container.  
* `name` is the name of the container. Arguments are supported.  
* `volumes` is a mapping of volume names and mountpoints inside the container. Arguments can be used inside 
the keys (volume names).  
* `ports` is a mapping of host ports and container ports. Arguments can be used in both keys and values.  
* `environment` is a mapping of environment variable names and values. Arguments can be used in the values.  

## Contributing
The default config contains setup flows for MongoDB and MySQL.
Feel free to add configs for other container types.
