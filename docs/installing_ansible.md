## Section 1: Install Python3, pip3 and Ansible
Open the terminal window. type pwd in the terminal and it should be showing you your home directory (/home/lab_user1) for example.
In the terminal window type the below commands one at a time.
```
mkdir Ansible_Workshop && cd Ansible_Workshop
sudo apt update
sudo apt install software-properties-common python3-pip python3-venv
```
Now we will create a new python virtual environment
```
python3 -m venv .venv
```
Activate the virtual environment
```
source .venv/bin/activate
```
Now that we are inside the python environment we can install packages here that will not affect our system python environment. This allows you to use different versions of ansible or other python packages that can potentially conflict. This also helps make your Ansible playbooks portable.

Now run the below command in terminal to install the packages
```
pip3 install wheel ansible pyats genie colorama 
```
Now that we have ansible installed we need to add a module that will help us connect and configure our topology
```
ansible-galaxy collection install cisco.ios clay584.genie
```