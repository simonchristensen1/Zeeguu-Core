# Zeeguu-Core 
[![Build Status](https://travis-ci.org/zeeguu-ecosystem/Zeeguu-Core.svg?branch=master)](https://travis-ci.org/zeeguu-ecosystem/Zeeguu-Core) 
[![Coverage Status](https://coveralls.io/repos/github/zeeguu-ecosystem/Zeeguu-Core/badge.svg?branch=master)](https://coveralls.io/github/zeeguu-ecosystem/Zeeguu-Core?branch=master)

The main model behind the zeeguu infrastructure.


# Installation

For installing on a fresh Ubuntu (16.04) run the `./ubuntu_install.sh` script.

For other OSs take inspiration from the aforementioned file, but skipping step 1. 

To be able to do anything meaningful with the Zeeguu-Core 
you must set the environment variable `ZEEGUU_CORE_CONFIG` 
to the path of a file which contains the info that's 
declared in `testing_default.cfg`. Only then can you start
working with zeeguu model elements by importing `zeeguu.model`. 

# Installing on Windows

1. git clone https://github.com/zeeguu-ecosystem/Zeeguu-Core.git
1. python -m venv zenv 
1. cd Zeeguu-Core
1. pip install -r requirements.txt
1. ./run_tests.sh


# Installing on Mac (Notes)
If you get an error like this: 

    ld: library not found for -lssl
    
when installing mysqlclient try to: 

    brew install openssl
    env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install mysqlclient
    
this is cf. https://stackoverflow.com/a/51701291/1200070








<!-- # Setup for Local Testing
6. Run `mysql -u root -p`
   1. Run `CREATE DATABASE zeeguu;`
   2. Run `exit`
6. Run `mysql.server start`
9. (Optional) You can populate the DB with the dataset that we used for the [CHI paper](https://github.com/zeeguu-ecosystem/CHI18-Paper/)
   1. download the [anonymized database dump](https://github.com/zeeguu-ecosystem/CHI18-Paper/blob/master/data/chi18_dataset_anon_2018-01-15.sql.zip) and unzip the file
   1. mysql -u root -p zeeguu < chi18_dataset_anon_2018-01-15.sql
   3. The database *should* be populated by now.
 -->

<!-- # MySQL

Install mysql and also the connection to python
```
apt-get install mysql-server libmysqlclient-dev python-mysqldb
```

# Project dev dependencies
```
apt-get install libxml2-dev libxslt1-dev
```
 -->
