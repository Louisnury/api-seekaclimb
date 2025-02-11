from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_models import User
from database import db

def register_user(userName, password):
    """Register a new user and return the user object"""
    if User.query.filter_by(name=userName).first():
        return None
    
    hashed_password = generate_password_hash(password)
    new_user = User(name=userName, password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'enregistrement: {str(e)}")
        
        return None

def authenticate_user(userName, password):
    """Authenticate a user and return a JWT token and user ID"""
    user = User.query.filter_by(name=userName).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return {
            'token': access_token,
            'user_id': user.id
        }
    return None

# Exporter explicitement les fonctions
__all__ = ['register_user', 'authenticate_user']
