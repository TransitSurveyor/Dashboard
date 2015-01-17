# Dashboard

#### setup
``` shell
# clone project
git clone https://github.com/TransitSurveyor/Dashboard.git
cd Dashboard

# create virtual environment and install python requirments
# some of the requirments may require other packages to be
# installed such as 'libpq-dev' and 'python-dev' being required for psycopg2
virtualenv env
env/bin/pip install -r requirements.txt

# copy and edit example config file for your environments settings
# project uses 'config.py' as default config file
cp example_config.py config.py

```


#### Deploying on Apache with mod_wsgi

1. create wsgi file
2. create virtual host
3. make wsgi file visible to apache user
