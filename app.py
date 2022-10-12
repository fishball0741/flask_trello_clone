from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

#it's for connect the database > protocol + adoptor:// user:password@ipaddress:port/db name
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:password123@127.0.0.1:5432/trello'
#direct using SQL
#ORM
# Flask app application
db = SQLAlchemy(app)

class Card(db.Model):   #Flask Alchemy data type , defining model
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  #can put max length inside the string, dont need to put () if no length required
    description = db.Column(db.Text)  #because text is better than string here, can put more words.
    date = db.Column(db.Date)  #be careful the date function. need to use the package from python, so import
    status = db.Column(db.String)
    priority = db.Column(db.String)

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

@app.cli.command('drop')
def drop_db():
    db.drop_all()
    print("Tables Dropped")


@app.cli.command('seed')
def seed_db():
    card = Card(
        title = 'Start the project',
        description = 'Stage 1 - Creating the database',
        status = 'To Do',
        priority = 'High',
        date = date.today()
    )
    #communication session with db, this momment, only add card, but normally can add more different things.
    # must be 'commit' it, otherwise cant go to the db really, Example, we can git add many times, and then do only one git commit in total to add all.
    #  commit to the database
    db.session.add(card)
    db.session.commit()
    print("Tables seeded")

# for listening the network,
@app.route('/')
def index():
    return "Hello World!"

