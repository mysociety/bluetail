if ! grep -q "cd /vagrant" ~/.bashrc ; then 
    echo "cd /vagrant/bluetail" >> ~/.bashrc 
fi 