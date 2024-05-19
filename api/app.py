from flask import Flask
from db import db
from api.routes import api_bp
from db.models import RecipientList, Recipient, EmailTemplate, Campaign

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Change to SQLite database URI

# Initialize SQLAlchemy
db.init_app(app)

# Register Blueprints
app.register_blueprint(api_bp)


def wipe_db():
    # Wipe the data from all tables
    print("@"*30)
    db.session.query(RecipientList).delete()
    db.session.query(Recipient).delete()
    db.session.query(EmailTemplate).delete()
    db.session.query(Campaign).delete()
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        wipe_db()
        if not any(table.query.first() for table in [RecipientList, Recipient, EmailTemplate, Campaign]):
            from db.dummy_data_initinilazier import create_dummy_data
            create_dummy_data()

    app.run(debug=True)
