# Bluetail

An alpha project combining beneficial ownership and contracting data, for use during government procurement.

Named after the [Himalayan Bluetail](https://en.wikipedia.org/wiki/Himalayan_bluetail) which was first described in 1845.

## Running this locally (with Vagrant)

Make sure to check out the submodules when you `git clone`:

```
git clone --recursive git@github.com:mysociety/bluetail.git
cd bluetail
```

Or to check out the submodules in a repo you’ve already cloned:

```
git submodule update --init
```

A Vagrantfile is included for local development. Assuming you have [Vagrant](https://www.vagrantup.com/) installed, you can create a Vagrant VM with:

```
vagrant up
```

Then SSH into the VM, and run the server script:

```
vagrant ssh
script/server
```

The site will be visible at <http://localhost:8000>.

Sass files are compiled by [django-pipeline](https://django-pipeline.readthedocs.io/en/latest/index.html), and CSS and JavaScript files are then copied to the `/static` directory by Django‘s [staticfiles](https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/) app.

The Django test server will compile and collect the static files automatically when it runs. But sometimes (eg: when you delete a file from `/web/sass/` and the change doesn’t seem to be picked up by the server) it might be necessary to force Django to re-process the static files. You force a full rebuild of the static files with:

```
script/manage collectstatic --noinput --clear
```


## Running this locally (without Vagrant)

You’ll need:

* Python 3.x
* A local Postgres server

As above, make sure you’ve cloned the repo and checked out its submodules.

Open up a Postgres shell (eg: `psql`) and create a user and database matching the details in `conf/config.py`:

```
CREATE USER bluetail SUPERUSER CREATEDB PASSWORD 'bluetail'
CREATE DATABASE bluetail
```

Create a Python virtual environment at a location of your choosing, activate it, and install the required packages:

```
python3 -m venv ./venv
. ./venv/bin/activate
pip3 install --requirement requirements.txt
```

With the virtual environment still activated, run the Django migrations, to set up the database:

```
script/migrate
```

And run the development server:

```
script/server
```


## Running this in production

The site requires:

* Python 3.5
* Django 2.2.8
* A Postgres database
