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


## Running this in production

The site requires:

* Python 3.5
* Django 2.2.8
* A Postgres database
