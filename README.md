# FeatureTrak

[![Travis](https://img.shields.io/travis/camilojd/FeatureTrak.svg?maxAge=2592000?style=flat-square)]()

A programming project for IWS based on https://github.com/IntuitiveWebSolutions/EngineeringMidLevel.

This project uses all IWS stack, including:

 * Python 2.7
 * Flask
 * Bootstrap 4
 * SQLAlchemy
 * MySQL
 * KnockoutJS
 * API testing with Python's `unittest`

### How to install and run

First, create a virtualenv and activate it:

```
(Fedora) virtualenv-2.7 ftenv
(Ubuntu LTS) virtualenv ftenv

source ftenv/bin/activate
```

Install MySQL:

```
(Fedora) sudo dnf install mariadb-server
(Ubuntu) sudo dnf apt-get install mysql-server
```

Clone the repo: 

```
git clone https://github.com/camilojd/featuretrak
```

To compile MySQL support for Python, in Ubuntu you may need to install the following two packages:
```
sudo apt-get install libmysqlclient-dev
sudo apt-get install python-dev
```

Inside the featuretrak folder, install pip requirements, create the database:

```
pip install -r requirements.txt
mysql -u root < create_database.sql
```

Create a new file named `instance/production.py` containing the production values for the configuration keys mentioned in `featuretrak/default_settings.py`, such as:

```
SQLALCHEMY_DATABASE_URI = 'mysql://enders:game@localhost/featuretrak'
GOOGLE_CLIENT_ID = 'The Google Client ID that was proportioned when registering the App @ Google'
SECRET_KEY = 'Some random string to secure Flask cookies'

```

To run the tests,
```
python api_tests.py
```

To load the initial data, and start/access the app
```
export FEATURETRAK_CONFIG=production.py
python create_initial_data.py
python app.py
```

And point your browser to http://localhost:5000
 
### Some general concepts

There are 2 types of users: admins (with access to the CRUD UI), and users that belong to a Client.

Clients have a numerical weight, and that weight may be based on the revenue or importance of that particular client. Features of clients with a bigger weight are ranked higher on a global list of all prioritized features.

It's possible to have both public and private "feature requests". Public feature requests can be backed by other clients and when more clients back them, they rank higher (according to each client's weight)

#### How ranking works

Rank of an an individual feature is calculated as follows:

 ` ((amount_features_in_client - cur_feature_priority) / amount_features_in_client) * client_weight`
 
 (priority starts from 0 at the feature with the highest priority).

Suppose we have one client, named *Draco*, with weight "1", and 3 features: X, Y, Z.
The rank of the first feature will be (((3 - 0) / 3) * 1) = 1, the second one (((3 - 1) / 3) * 1) = 0.66, and the third one (((3 - 2) / 3) * 1) = 0.33.

Then, a new deal is made with a client named *Infinia* having a weight of 1.5, and that clients asks the development of 2 features, M and N. The rank of the first feature will be (((2 - 0) / 2) * 1.5) = 1.5, the second one (((2 - 1 ) / 2) * 1.5) = 0.75

So the final ranking of features will be as below:

| Client        | Feature       | Rank  |
| ------------- |---------------| -----:|
| Infinia       | M             | 1.500 |
| Draco         | X             | 1.000 |
| Infinia       | N             | 0.750 |
| Draco         | Y             | 0.666 |
| Draco         | Z             | 0.333 |


### Some implementation details

All the "CRUD" entities and features are accesible through a RESTful interface:

`GET /api/v1/features` (plural) to obtain all features.

`POST /api/v1/feature` (singular) to create a new feature.

`GET | PUT | DELETE /api/v1/feature/1` (singular) to obtain an specific feature, modify or delete it.

Same thing applies for admin entities(`areas, users, clients`), but prepending `/admin`, like: `/api/v1/admin/areas`

Successful requests return status code 200. Non authorized requests 403 and validation failure requests 409.

