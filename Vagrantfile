# -*- mode: ruby -*-
# vi: set ft=ruby :

# Checks for vagrant-docker-compose plugin and installs it if missing
unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/trusty64"

  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 1
  end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y git python-pip python-dev build-essential
    sudo apt-get -y autoremove
    # Install the Cloud Foundry CLI
    wget -O cf-cli-installer_6.22.1_x86-64.deb 'https://cli.run.pivotal.io/stable?release=debian64&version=6.22.1&source=github-rel'
    sudo dpkg -i cf-cli-installer_6.22.1_x86-64.deb
    rm cf-cli-installer_6.22.1_x86-64.deb
    # Install app dependencies
    cd /vagrant
    sudo pip install -r requirements.txt
    # Prepare Redis data share
    sudo mkdir -p /var/lib/redis/data
    sudo chown vagrant:vagrant /var/lib/redis/data
    # Make vi look nice
    echo "colorscheme desert" > ~/.vimrc
  SHELL
  # Provision docker
  config.vm.provision :docker

  # Install Docker Compose after Docker Engine
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    sudo pip install docker-compose
    # Install the IBM Container plugin
    echo Y | cf install-plugin https://static-ice.ng.bluemix.net/ibm-containers-linux_x64
  SHELL
  
  # Run docker-compose to build and link docker containers. NOTE - this requires the vagrant plugin vagrant-docker-compose
  config.vm.provision :docker_compose, yml: "/vagrant/docker-compose.yml",rebuild: true, command_options: { rm: "", up: "-d --timeout 20"}, run: "always"

end
