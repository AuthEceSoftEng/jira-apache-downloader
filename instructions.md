# Dataset Installation Instructions
Setting up the dataset requires a running MongoDB instance. In this text, we describe a configuration for downloading,
and installing MongoDB in Ubuntu 18.04 (the installation for any other OS is similar), as well as instructions for retrieving
and setting up the dataset. The readme of this repo provides instructions for using the tool of this repo for connecting to the database.

## Installing MongoDB
1. Import the public key used by the package management system.  
`wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -`

2. Create a list file for MongoDB.  
`echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list`

3. Issue the following command to reload the local package database:  
`sudo apt-get update`

4. Install the MongoDB packages.  
`sudo apt-get install -y mongodb-org`

5. To prevent unintended upgrades (optional), you can pin the package at the currently installed version:

```
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
```

6. Enable mongo to add to startup and start it:

```
sudo systemctl enable mongod
sudo systemctl start mongod
```

7. Create users (one admin user to read/write and one user to only read) by running `mongo` to access the mongo shell and executing the commands (change usernames and passwords to your own):

```
use admin;
db.createUser({ user: "ADMINNAME", pwd: "ADMINPASSWORD", roles: [ { role: "userAdminAnyDatabase", db: "ADMINNAME" }, { role: "readWriteAnyDatabase", db: "ADMINNAME" }, { role: "dbAdminAnyDatabase",   db: "ADMINNAME" } ] });
db.createUser({user: "USERNAME", pwd: "USERPASSWORD", roles: [{role: "read", db: "jidata"}]})
```

8. Enable MongoDB Auth by opening the configuration (`sudo nano /etc/mongod.conf`) and adding the lines:

```
security:
    authorization: 'enabled'
```

Also, change the network interfaces to allow accessing the database from outside localhost:

```
net:
    port: 27017
    bindIp: 0.0.0.0   #default value is 127.0.0.1
```

And restart using `sudo systemctl restart mongod`

## Downloading the Data and Populating the Database
Run the following commands to instantiate the db:

```
mkdir dump
wget -O dump/commits.bson.gz https://zenodo.org/record/5665896/files/comments.bson.gz?download=1
wget -O dump/comments.metadata.json.gz https://zenodo.org/record/5665896/files/comments.metadata.json.gz?download=1
wget -O dump/events.bson.gz https://zenodo.org/record/5665896/files/events.bson.gz?download=1
wget -O dump/events.metadata.json.gz https://zenodo.org/record/5665896/files/events.metadata.json.gz?download=1
wget -O dump/issues.bson.gz https://zenodo.org/record/5665896/files/issues.bson.gz?download=1
wget -O dump/issues.metadata.json.gz https://zenodo.org/record/5665896/files/issues.metadata.json.gz?download=1
wget -O dump/projects.bson.gz https://zenodo.org/record/5665896/files/projects.bson.gz?download=1
wget -O dump/projects.metadata.json.gz https://zenodo.org/record/5665896/files/projects.metadata.json.gz?download=1
wget -O dump/users.bson.gz https://zenodo.org/record/5665896/files/users.bson.gz?download=1
wget -O dump/users.metadata.json.gz https://zenodo.org/record/5665896/files/users.metadata.json.gz?download=1
wget -O dump/worklogs.bson.gz https://zenodo.org/record/5665896/files/worklogs.bson.gz?download=1
wget -O dump/worklogs.metadata.json.gz https://zenodo.org/record/5665896/files/worklogs.metadata.json.gz?download=1
mongorestore -h localhost:27017 -d gddata -u ADMINNAME -p ADMINPASSWORD --gzip dump/
```

