from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from extensions import db
from models import Pet
import os
import logging
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Create a Blueprint with a URL prefix
api = Blueprint('api', __name__, url_prefix='/api')

# Enable CORS
CORS(app)

# Load DB config from environment variables
DB_HOST = os.getenv('DB_HOST', 'db.petstore.internal')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'petstore')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD')

logger.info(f"DB Config: host={DB_HOST}, port={DB_PORT}, name={DB_NAME}, user={DB_USER}")

# Log all environment variables for debugging
logger.info(f"Loaded environment variables: {os.environ}")

# Check if DB_PASSWORD is missing
if not DB_PASSWORD:
    logger.error("DB_PASSWORD environment variable is not set!")
    raise ValueError("DB_PASSWORD environment variable is not set!")

# URL encode password to handle special characters
encoded_password = quote_plus(DB_PASSWORD)

# Configure SQLAlchemy for MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create the database tables
try:
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
        if not Pet.query.first():
            logger.info("Pre-populating database with sample data...")
            pets = [
                Pet(name='Buddy', type='Dog', price=300),
                Pet(name='Mittens', type='Cat', price=150),
                Pet(name='Goldie', type='Fish', price=25),
                Pet(name='Tweety', type='Bird', price=50),
            ]
            db.session.add_all(pets)
            db.session.commit()
            logger.info("Database pre-populated successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Routes
@api.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets])

@api.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return jsonify(pet.to_dict())

@api.route('/pets', methods=['POST'])
def add_pet():
    data = request.json
    new_pet = Pet(name=data['name'], type=data['type'], price=data['price'])
    db.session.add(new_pet)
    db.session.commit()
    return jsonify(new_pet.to_dict()), 201

@api.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    data = request.json
    pet.name = data.get('name', pet.name)
    pet.type = data.get('type', pet.type)
    pet.price = data.get('price', pet.price)
    db.session.commit()
    return jsonify(pet.to_dict())

@api.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return '', 204

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Register the Blueprint
app.register_blueprint(api)

if __name__ == '__main__':
    logger.info("Starting Flask app...")
    app.run(debug=True)