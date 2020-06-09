# -*- mode: ruby -*-
# vi: set ft=ruby :


# add secret key to local vagrant profile
SECRET_KEY = ENV.fetch('BLUETAIL_SECRET_KEY', 'default_secret_key')
DATABASE_URL = ENV.fetch('DATABASE_URL', 'postgres://bluetail:bluetail@localhost:5432/bluetail')

Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "sagepe/stretch"

  config.vm.synced_folder ".", "/vagrant/bluetail/"

  # Speed up DNS lookups
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
  end

  # Django dev server
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 1080, host: 1080

  # Give the VM a bit more power to speed things up
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 1
  end

  # Provision the vagrant box
  config.vm.provision "shell", env: {"SECRET_KEY" => SECRET_KEY}, inline: <<-SHELL
		 if ! grep -q "SECRET_KEY" ~/.bashrc ; then
			  echo "export SECRET_KEY=$SECRET_KEY" >> /home/vagrant/.bashrc
		fi
	  SHELL
  config.vm.provision "shell", env: {"DATABASE_URL" => DATABASE_URL}, inline: <<-SHELL
		  if ! grep -q "DATABASE_URL=" ~/.bashrc ; then
			  echo "export DATABASE_URL=$DATABASE_URL" >> /home/vagrant/.bashrc
		fi
	  SHELL

  config.vm.provision "shell", env: {"DATABASE_URL" => DATABASE_URL}, inline: <<-SHELL
	sudo apt-get update

    cd /vagrant/bluetail

    #fix dpkg-preconfigure error
    export DEBIAN_FRONTEND=noninteractive
    
    # Install the packages from conf/packages
    xargs sudo apt-get install -qq -y < conf/packages
	xargs sudo apt-get install -qq -y < conf/dev_packages
    # Install some of the other things we need that are just for dev
    sudo apt-get install -qq -y ruby-dev libsqlite3-dev build-essential

    # Create a postgresql user
    sudo -u postgres psql -c "CREATE USER bluetail SUPERUSER CREATEDB PASSWORD 'bluetail'"
    # Create a database
    sudo -u postgres psql -c "CREATE DATABASE bluetail"

    # Run post-deploy actions script to update the virtualenv, install the
    # python packages we need, migrate the db and generate the sass etc
    script/bootstrap

	# give permissions to vagrant user on all the packages
	sudo chmod -R ugo+rwx /vagrant/venv
  SHELL

  # Automatically `cd /vagrant/bluetail` on `vagrant ssh`.
  config.ssh.extra_args = ["-t", "cd /vagrant/bluetail; bash --login"]

end
