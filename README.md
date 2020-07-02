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


## Deployment to Heroku

These environment variables must be set on the Heroku app before deployment.

    DJANGO_SETTINGS_MODULE=proj.settings_heroku
    DATABASE_URL="postgres://..."
    SECRET_KEY=""
    
Run migrations on Heroku like this:

    heroku run "script/migrate" --app [heroku app name]
    

## Adding example data to database

There is included dummy data for demonstrating the app. 
Run this command to insert it to your database.

    script/insert_example_data

or on heroku
    
    heroku run "script/insert_example_data" --app [heroku app name]

    
## Viewing example data

There are basic endpoints for viewing the sample data by ID

OCDS release

http://127.0.0.1:8000/ocds/ocds-123abc-PROC-20-0001/

BODS statements

http://localhost:8000/bods/statement/person/17bfeb0d-4a63-41d3-814d-b8a54c81a1i/
http://localhost:8000/bods/statement/entity/1dc0e987-5c57-4a1c-b3ad-61353b66a9b1/
http://localhost:8000/bods/statement/ownership/676ce2ec-e244-409e-85f9-9823e88bc003/


### Filtering the dataset

Each dataset has a distinct OCID prefix, as with publishers of real data.

https://standard.open-contracting.org/latest/en/schema/identifiers/#contracting-process-identifier-ocid

We can filter our tender listing to a specific dataset by specifying a prefix in the HTML parameter `ocid_prefix`:

For example:

    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-b5fd17
    
####Prefixes used in the sample data:

Prototype data:

    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-123abc-

Contracts Finder data linked to Companies House where suppliers have a matching BODS record:

    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-b5fd17bodsmatch
    
Contracts Finder data including only suppliers which can be linked to Companies House:

    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-b5fd17suppliermatch
    
Contracts Finder data with suppliers linked to Companies House and an ID included where a match exists:

    http://127.0.0.1:8000/ocds/?ocid_prefix=ocds-b5fd17raw

## Flags

Flags are warnings/errors about the data, attached to an individual or company.

Flag

Flags can be viewed and edited in the admin interface

    http://127.0.0.1:8000/admin/

If you don't have a superuser, create one manually like this

    python manage.py createsuperuser
    
or without prompt (username: admin, password: admin)

    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')" | python manage.py shell

### Scanning contracts for potential problems

There is a management command, `scan_contracts`, which looks through all
contracts and flags up any suspicious activity. In production this command
should be run on a regular basis to check for any new problems.

### Deployment to Heroku 

The Heroku-GitHub integration does not work with `git-submodules` 
(Related issue in Notion: https://www.notion.so/spendnetwork/Fix-COLLECTSTATIC-on-Heroku-deployment-814cd676c81c41aba1b622b4a8a161bb)

So to deploy we need to push to the Heroku `bluetail` app git remote manually.

This is easiest done using the Heroku CLI tools. https://devcenter.heroku.com/articles/heroku-cli

1. Log in to Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli#getting-started)
2. Add the Heroku app git remote to your git clone
    
    Execute this command in your bluetail clone root directory
            
        heroku git:remote --app bluetail

3. Force push your branch to the Heroku remote `master` branch.

        git push heroku master:master --force
        
    3. Note you can push any local branch, but it must be pushed to the Heroku remote `master` branch to deploy. 
        
            git push heroku [local_branch_to_push]:master --force

4. (Optional) Run the setup script to reset the Heroku database.

        heroku run "script/setup"

### Testing

There are just a few tests written to aid development. 
To run use this command

    script/manage test
    
    