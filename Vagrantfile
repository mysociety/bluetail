# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'fileutils'

#copy config example if not done manually
if not File.exists?('conf/config.py')
	FileUtils.cp('conf/config_example.py,'conf/config.py')
end

Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "sagepe/stretch"

  # Enable NFS access to the disk
  config.vm.synced_folder ".", "/vagrant/bluetail/", :nfs => true

  # Speed up DNS lookups
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
  end

  # NFS requires a host-only network
  # This also allows you to test via other devices (e.g. mobiles) on the same
  # network
  config.vm.network :private_network, ip: "10.11.12.13"

  # Django dev server
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 1080, host: 1080

  # Give the VM a bit more power to speed things up
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 1
  end

  # Provision the vagrant box
  config.vm.provision "shell", path: "conf/provisioner.sh", privileged: false
  config.vm.provision "shell", inline: <<-SHELL
	sudo apt update

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
    conf/post_deploy_actions.bash

	# give permissions to vagrant user on all the packages
	sudo chmod -R ugo+rwx /vagrant/venv
  SHELL

end
