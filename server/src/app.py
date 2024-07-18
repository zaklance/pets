# our main flask app
# API == Application Programing Interface

# can start flask with
# flask --app src/app.py run --port 5555 --debug

# can also use env vars (don't commit the .env file!!!)
# export FLASK_APP=src/app.py
# export FLASK_RUN_PORT=5555
# export FLASK_DEBUG=1
# flask run


# CRUD == Create, Read, Update, Delete
# HTTP verbs: POST, GET, PATCH (PUT), DELETE
# ReST

# how to set up .env file
# pipenv install python-dotenv
# create a .env where the Pipfile is
# add ".env" to .gitignore (create .gitignore if not already exists)
# add keys to .env file (ex: FLASK_APP=src/app.py)
# import into python with:
# import os
# os.environ['KEY_NAME']

# create a secret key: python -c 'import os; print(os.urandom(16))'

import os
from flask import Flask, request, make_response, jsonify, session, render_template
from models import db, Pet, Owner, User
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(
    __name__,
    static_url_path='',
    static_folder='../../client/my-app/dist',
    template_folder='../../client/my-app/dist'
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']  # how to connect to the db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # optional performance thing
app.secret_key = os.environ['SECRET_KEY'] # grab the secret key from env variables


db.init_app(app)  # link sqlalchemy with flask
Migrate(app, db)  # set up db migration tool (alembic)
CORS(app, supports_credentials=True)  # set up cors


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

@app.route('/')
def hello():
    json_string = jsonify({'test': 'hello'})  # turn dict into json
    web_resp = make_response(json_string, 200)  # build a web resp
    return web_resp


@app.route('/api/dogs')
def dogs():
    # query db for all dog pets
    all_dogs = Pet.query.filter(Pet.type == 'dog').all()
    all_dog_dicts = [d.to_dict() for d in all_dogs]  # turn all dog objs into dicts
    return all_dog_dicts, 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()  # get user data

    # check if the user exists
    user = User.query.filter(User.username == data['username']).first()
    if not user:
        return {'error': 'login failed'}, 401
    
    # check if password can generate the same hash
    if not user.authenticate(data['password']):
        return {'error': 'login failed'}, 401
    
    # set browser cookie
    session['user_id'] = user.id

    return user.to_dict(), 200

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # check if the user already exists
    user = User.query.filter(User.username == data['username']).first()
    if user:
        return {'error': 'username already exists'}, 400

    new_user = User(
        username=data['username'], 
        password=data['password']
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user.to_dict(), 201

@app.route('/api/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)  # remove the login cookie (None prevents the key error)
    return {}, 204

@app.route('/api/check_session')
def check_session():
    # get the cookie
    user_id = session.get('user_id')

    if not user_id:
        # no cookie set, user is not logged in
        return {'error': 'authorization failed'}, 401
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        # cookie is invalid
        return {'error': 'authorization failed'}, 401
    
    return user.to_dict(), 200

@app.route('/api/pets', methods=['GET', 'POST'])
def all_pets():
    t = get_all_owners()
    print(t[0])
    if request.method == 'GET':
        pets = Pet.query.all()
        return [p.to_dict() for p in pets], 200
    elif request.method == 'POST':
        # grab json data from request (as dict)
        data = request.get_json()

        # build new pet obj
        try:  # try to run this block of code
            new_pet = Pet(
                name=data.get('name'),
                age=data.get('age'),
                type=data.get('type'),
                owner_id=data.get('owner_id')
            )
        except ValueError as e:
            # if a ValueError is raise above, run this code
            return {'error': str(e)}, 400

        # save new pet obj to the db
        db.session.add(new_pet)
        db.session.commit()

        return new_pet.to_dict(), 201


@app.route('/api/pets/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def pet_by_id(id):
    pet = Pet.query.filter(Pet.id == id).first()

    if not pet:
        return {'error': 'pet not found'}, 404
    
    if request.method == 'GET':
        return pet.to_dict(), 200
    elif request.method == 'PATCH':
        # get json data from request
        data = request.get_json()

        # option 1, check every single field
        # if 'name' in data:
        #     pet.name = data['name']
        # if 'age' in data:
        #     pet.age = data['age']
        # if 'type' in data:
        #     pet.type = data['type']

        # option 2, loop through json keys and use setattr to update the attribute on the object
        for field in data:
            # pet.field = data[field]  # this doesn't work
            try:
                setattr(pet, field, data[field])
            except ValueError as e:
                return {'error': str(e)}, 400


        db.session.add(pet)
        db.session.commit()

        return pet.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(pet)
        db.session.commit()

        return {}, 204


@app.get('/api/owners')  # @app.route('/owners', methods=['GET'])
def get_all_owners():
    owners = Owner.query.all()
    return [o.to_dict() for o in owners], 200

@app.post('/api/owners') # @app.route('/owners', methods=['POST'])
def post_owner(): 
    pass