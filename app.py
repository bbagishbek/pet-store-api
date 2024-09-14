from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db
from models import Pet

app = Flask(__name__)

# Enable CORS
CORS(app)  # Allow all domains

# Alternatively, specify the origin
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()
    # Optional: Pre-populate the database
    if not Pet.query.first():
        pets = [
            Pet(name='Buddy', type='Dog', price=300),
            Pet(name='Mittens', type='Cat', price=150),
            Pet(name='Goldie', type='Fish', price=25),
            Pet(name='Tweety', type='Bird', price=50),
        ]
        db.session.add_all(pets)
        db.session.commit()

# Get all pets
@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets])

# Get a single pet
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return jsonify(pet.to_dict())

# Add a new pet
@app.route('/pets', methods=['POST'])
def add_pet():
    data = request.json
    new_pet = Pet(name=data['name'], type=data['type'], price=data['price'])
    db.session.add(new_pet)
    db.session.commit()
    return jsonify(new_pet.to_dict()), 201

# Update an existing pet
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    data = request.json
    pet.name = data.get('name', pet.name)
    pet.type = data.get('type', pet.type)
    pet.price = data.get('price', pet.price)
    db.session.commit()
    return jsonify(pet.to_dict())

# Delete a pet
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
