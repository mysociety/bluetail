# -*- mode: ruby -*-
# vi: set ft=ruby :


# add secret key to local vagrant profile
# either use hosts BLUETAIL_SECRET_KEY variable or a quick local one

secret_key_value = ENV.fetch('BLUETAIL_SECRET_KEY', 'default_secret_key')
env_var_cmd = <<CMD
echo "export SECRET_KEY=#{secret_key_value}" | tee -a /home/vagrant/.profile
CMD

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
  config.vm.provision "shell", :inline => env_var_cmd
  config.vm.provision "shell", path: "conf/provisioner.sh", privileged: false
  config.vm.provision "shell", env: {"SECRET_KEY" => secret_key_value}, inline: <<-SHELL
	sudo apt update

    cd /vagrant/bluetail

    #fix dpkg-preconfigure error
    export DEBIAN_FRONTEND=noninteractive
    
    # Install the packages from conf/packages
    xargs sudo apt-get install -qq -y < conf/packages
	xargs sudo apt-get install -qq -y < conf/dev_packages
    # Install some of the other things we need that are just for dev
    sudo apt-get install -qq -y ruby-dev libsqlite3-dev build-essential

    # TODO: We should use script/setup here!

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
