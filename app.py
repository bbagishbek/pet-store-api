from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from extensions import db
from models import Pet
import os

app = Flask(__name__)

# Create a Blueprint with a URL prefix
api = Blueprint('api', __name__, url_prefix='/api')

# Enable CORS
CORS(app)  # Allow all domains

# Load DB config from environment variables (set by ECS)
DB_HOST = os.getenv('DB_HOST', 'db.petstore.internal')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'petstore')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Must be set in ECS secrets

# Configure SQLAlchemy for MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Check if DB_PASSWORD is missing
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is not set!")

db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()
    # Optional: Pre-populate the database (only if empty)
    if not Pet.query.first():
        pets = [
            Pet(name='Buddy', type='Dog', price=300),
            Pet(name='Mittens', type='Cat', price=150),
            Pet(name='Goldie', type='Fish', price=25),
            Pet(name='Tweety', type='Bird', price=50),
        ]
        db.session.add_all(pets)
        db.session.commit()

# 🛠 Move Routes Inside the Blueprint
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

# ✅ Register the Blueprint in the main app
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)
