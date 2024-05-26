from flask import Flask
from db import db
from db.models import RecipientList, Recipient, EmailTemplate, Campaign
from db.dummy_data_initinilazier import create_dummy_data
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Change to SQLite database URI

# Initialize SQLAlchemy
db.init_app(app)


def seed_data():
    with app.app_context():
        # Create tables
        logging.debug("Creating database tables...")
        db.create_all()

        # Seed data
        logging.debug("Seeding data...")
        wipe_db()
        if not any(table.query.first() for table in [RecipientList, Recipient, EmailTemplate, Campaign]):
            create_dummy_data()


def wipe_db():
    # Wipe the data from all tables
    logging.debug("Wiping database tables...")
    db.session.query(RecipientList).delete()
    db.session.query(Recipient).delete()
    db.session.query(EmailTemplate).delete()
    db.session.query(Campaign).delete()
    db.session.commit()


if __name__ == "__main__":
    seed_data()
    logging.debug("Data seeding completed.")
