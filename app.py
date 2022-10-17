from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config ['JSON_SORT_KEYS'] = False

#it's for connect the database > protocol + adoptor:// user:password@ipaddress:port/db name
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello'
#direct using SQL
#ORM
# Flask app application
db = SQLAlchemy(app)
ma = Marshmallow(app)

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
    cards = [
        Card(
            title = 'Start the project',
            description = 'Stage 1 - Creating the database',
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
    #communication session with db, this momment, only add card, but normally can add more different things.
    # must be 'commit' it, otherwise cant go to the db really, Example, we can git add many times, and then do only one git commit in total to add all.
    #  commit to the database
    db.session.add_all(cards)
    db.session.commit()
    print("Tables seeded")

# can terminal  >  flask drop && flask create && flask seed  < to do all

@app.route('/cards/')
def all_cards():
    # select * from cards;
    # cards = Card.query.all()
    # stmt = db.select(Card).where(Card.status == 'To Do')
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)
    # for card in cards:
    #     print(card.title, card.priority)
    # print(cards)
    # print(cards[0].__dict__)

@app.cli.command('first_card')
def first_card():
    # select * from cards limit 1;
    # card = Card.query.first()
    stmt = db.select(Card).limit(1)
    card = db.session.scalar(stmt)
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

