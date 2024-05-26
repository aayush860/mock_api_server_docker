from flask import Flask
from api.routes import api_bp
from db import db
from db import data_seed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Change to SQLite database URI

# Initialize SQLAlchemy
db.init_app(app)

# Register Blueprints
app.register_blueprint(api_bp)

if __name__ == '__main__':
    data_seed.seed_data()
    app.run(debug=True)
