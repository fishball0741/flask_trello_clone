from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta   #timedelta = limited the token time(allows the period of time in any units we want, make them will expire in the specify day)
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt   #for encrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, create_access_token, jwt_required    # jwt extension can generate the toker for flask and json


app = Flask(__name__)
app.config ['JSON_SORT_KEYS'] = False

#it's for connect the database > protocol + adoptor:// user:password@ipaddress:port/db name
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello'
app.config['JWT_SECRET_KEY'] = 'hello there'   #for create a secret key for encrypt the token. generate a random token, but when will making an app, maybe using the fix code
#direct using SQL
#ORM
# Flask app application
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)  #false mean cannot null, must write the email.   unique = only can register one
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)   #admin had authorization, so no default.

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'is_admin')   # know we need password but not it json.
    


class Card(db.Model):   #Flask Alchemy data type , defining model
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  #can put max length inside the string, dont need to put () if no length required
    description = db.Column(db.Text)  #because text is better than string here, can put more words.
    date = db.Column(db.Date)  #be careful the date function. need to use the package from python, so import
    status = db.Column(db.String)
    priority = db.Column(db.String)

class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'status', 'priority', 'date')
        ordered = True

# go to each model, in each model, it will go to check the db and see any table already exists in db, if exists then skip, if not it will create it.
# RuntimeError: Working outside of application context.  
# db.create_all()   

# cli.command = custom command for Flask in terminal
# Defining a custom CLI (Terminal) command
# for listening on the terminal
@app.cli.command('create')
def create_db():
    db.create_all()
    print("Tables Created")


# drop all tables
@app.cli.command('drop')
def drop_db():
    db.drop_all()
    print("Tables Dropped")


@app.cli.command('seed')
def seed_db():
    users = [
        User(
            email='admin@spam.com',
            password=bcrypt.generate_password_hash('eggs').decode('utf-8'),
            is_admin=True
        ),
        User(
            name='John',
            email='someone@spam.com',
            password=bcrypt.generate_password_hash('12345').decode('utf-8'),
        )
    ]

    cards = [
        Card(
            title = 'Start the project',
            description = 'Stage 1 - Create the database',
            status = 'To Do',
            priority = 'High',
            date = date.today()
        ),
        Card(
            title = "SQLAlchemy",
            description = "Stage 2 - Integrate ORM",
            status = "Ongoing",
            priority = "High",
            date = date.today()
        ),
        Card(
            title = "ORM Queries",
            description = "Stage 3 - Implement several queries",
            status = "Ongoing",
            priority = "Medium",
            date = date.today()
        ),
        Card(
            title = "Marshmallow",
            description = "Stage 4 - Implement Marshmallow to jsonify models",
            status = "Ongoing",
            priority = "Medium",
            date = date.today()
        )
    ]

    db.session.add_all(cards)
    db.session.add_all(users)
    db.session.commit()
    print('Tables seeded')


@app.route('/auth/register/', methods=['POST'])    #because we want this route should be POST request instead of route, so set the method to POST
def auth_register():  #encode and python object, can use json to convert as well
    try:
        # Load the posted user info and parse the JSON
        # user_info = UserSchema().load(request.json)   #need to request data
        # print(user_info)
        # Create a new User Model instance from the user_info
        user = User(
            email = request.json['email'],     #those using [ ] instead of  user_info.email  < can't use it
            password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),    #encrypt the password, hash the password
            name = request.json['name']
        )
        # add and commit user to DB
        db.session.add(user)
        db.session.commit()
        # respond to client
        return UserSchema(exclude=['password']).dump(user), 201   #normally use 201     , need to exculde the password here as dont want to show the password hash

        # In this case (complex multi-running flow) after client input, will check the db, and see any data already in the database, if yes, then return the error
    except IntegrityError:
        return {'error': 'Email address already in use'}, 409



# Login route  only for POST
@app.route('/auth/login/', methods=['POST'])   
def auth_login():   #check any account/email/user name in DB first.
    #  Find a use by email address
    stmt = db.select(User).filter_by(email=request.json['email'])   # or using  db.select(User).where(User.email == request.json['email'])  < comparison, so need  ==
    user = db.session.scalar(stmt)

    # create a statement first  ,  and search the email and password (CANNOT USE generate_password_hash) >>> the generate_salt will produce random, so can't match the original pw hash
    # check_password_hash        
    # If user exists and password is correct  
    if user and bcrypt.check_password_hash(user.password, request.json['password']):
        # return UserSchema(exclude=['password']).dump(user)   #200 = default
        #what we want to identity for the user, by email? by the ID number?
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))    #set the id will be a string from user.id, and expires in one days
        return {'email': user.email, 'token': token, 'is_admin': user.is_admin}   #using this instead of Schema because we dont want to return all the details and also want to have token.
    # If user exists and password is not correct,   security reason, dont specifically say what's wrong, pw or email.
    else:
        return {'error': 'Invalid password or email'}, 401

# can terminal  >  flask drop && flask create && flask seed  < to do all

@app.route('/cards/')
@jwt_required()
def all_cards():
    # select * from cards;
    # cards = Card.query.all()
    # stmt = db.select(Card).where(Card.status == 'To Do')
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)   # statement =stmt
    cards = db.session.scalars(stmt)  # same as execute , to the statement,  ( different when choose certain columns, but scalars is better)
    return CardSchema(many=True).dump(cards)  # we used scalars, we know will show a list, 
    # for card in cards:
    #     print(card.title, card.priority)
    # print(cards)
    # print(cards[0].__dict__)

@app.cli.command('first_card')
def first_card():
    # select * from cards limit 1;
    # card = Card.query.first()
    stmt = db.select(Card).limit(1)
    card = db.session.scalars(stmt)
    print(card.__dict__)

@app.cli.command('count_ongoing')
def count_ongoing():
    stmt = db.select(db.func.count()).select_from(Card).filter_by(status='Ongoing')
    cards = db.session.scalar(stmt)
    print(cards)


# for listening the network,
@app.route('/')
def index():
    return "Hello World!"

