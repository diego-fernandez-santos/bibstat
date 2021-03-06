# Serverkonfiguration

Detta dokument sammanfattar hur stage- och produktionsmiljön sattes upp.

    # 1. Add environment variables to ~/.bashrc
    export LC_ALL=en_US.UTF-8
    export LD_LIBRARY_PATH=/usr/local/lib
    export LD_RUN_PATH=/usr/local/lib
    export CFLAGS="$CFLAGS -fPIC"

    # 2. Reload ~/.bashrc
    source ~/.bashrc

    # 3. Install required libs prior to building python
    yum install bzip2 bzip2-devel

    # 4. Install python2.7
    wget http://www.python.org/ftp/python/2.7.5/Python-2.7.5.tgz
    tar xvf Python-2.7.5.tgz
    cd Python-2.7.5

    ./configure --enable-shared --with-threads
    make
    make install

    cd ..
    rm -rf Python-2.7.5
    rm -f Python-2.7.5.tgz

    # 5. Install Apache and python tools
    yum install httpd httpd-devel python-pip python-virtualenv

    # 6. Install mod_wsgi and make sure it uses python2.7
    wget http://modwsgi.googlecode.com/files/mod_wsgi-3.4.tar.gz
    tar xvf mod_wsgi-3.4.tar.gz
    cd mod_wsgi-3.4

    ./configure  --with-python=/usr/local/bin/python2.7
    make
    make install

    cd ..
    rm -rf mod_wsgi-3.4
    rm -f mod_wsgi-3.4.tar.gz

    # 7. Add this to file /etc/yum.repos.d/mongodb.repo
    [mongodb]
    name=MongoDB Repository
    baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
    gpgcheck=0
    enabled=1

    # 8. Create this directory, mongo needs it
    mkdir /data/db

    # 9. Install mongo
    yum install mongodb-org

    # 10. Make sure that these lines in /etc/mongod.conf are commented out and inactive
    bind_ip = 127.0.0.1
    auth = true

    # 11. Start mongo
    service mongod start

    # 12. Create admin user
    mongo
    > use admin
    > db.createUser({user:"admin", pwd:"admin", roles: ["root"]})
    > db.runCommand({usersInfo:"admin", showPrivileges:true })

    # 13. Restart mongo
    service mongod restart

    # 14. Double check that authentication is working
    mongo admin
    > db.auth("admin", "admin")

    # 15. Create bibstat user
    mongo 
    > use bibstat
    > db.createUser({user:"bibstat", pwd:"<password>", roles:["readWrite"]})
    > db.runCommand({usersInfo:"bibstat", showPrivileges:true })

    # 16. Export dump from mongo on old prod bibstat machine
    mongodump -d bibstat -u bibstat -p <password>

    # 17. Transfer the dump from the old to the new prod bibstat machine
    scp -r dump root@<hostname>:/tmp/bibstat-prod-dump

    # 18. Load the dump on the new prod machine
    mongorestore -u admin -p admin /tmp/bibstat-prod-dump/

    # 19. Add this to /etc/httpd/conf.d/bibstat.conf
    LoadModule wsgi_module modules/mod_wsgi.so 
    <VirtualHost *:80>
            ServerName      <hostname>
            ServerAdmin     niklas.lindstrom@kb.se

            Alias /static /data/appl/bibstat/static

            WSGIDaemonProcess       bibstat python-path=/data/appl/bibstat:/data/appl/bibstat/env/lib/python2.7/site-packages processes=16 threads=4
            WSGIScriptAlias         / /data/appl/bibstat/bibstat/wsgi.py
            WSGIProcessGroup        bibstat
            WSGIApplicationGroup    %{GLOBAL}

            ErrorLog        logs/bibstat-error_log
            CustomLog       logs/bibstat-access_log combined

            RewriteEngine on
            RewriteRule ^/.well-known/void$ /open_data/ [R]
    </VirtualHost>

    # 20. Create deployment target folder and grant everyone read-write-rights
    mkdir /data/appl
    chmod a+rw /data/appl

    # 21. Prepare settings that will be symlinked into deployed repo
    # Create file /data/appl/config/bibstat_local.py and add to it (making sure to keep the secret key for production environments a secret!):
    SECRET_KEY = '3x%=t4cm@eszqbwuw@00f**ol@8^kqomtm8-%x&5_ydq9rm(nl'
    DEBUG = False
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = [
        ".<hostname>",
        ".<hostname>.",
    ]
    API_BASE_URL = "http://<hostname>/statistics"
    BIBDB_BASE_URL = "http://bibdb.libris.kb.se"
    MONGODB_HOST = 'localhost'
    MONGODB_NAME = 'bibstat'
    MONGODB_USER = 'bibstat'
    MONGODB_PASSWD = '<password>'

    # 22. Link virtualenv to /usr/local/bin/ to make deployment scripts happy
    ln -s $(which virtualenv) /usr/local/bin/

    # 23. "Push" code from local machine to bibstat
    fab conf.prodbibstat app.bibstat.deploy_without_sudo 

    # 24. Restart apache server
    service httpd restart

    # 25. Test that the service is up and running
    wget "http://localhost"