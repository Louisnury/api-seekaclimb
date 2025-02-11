from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from dotenv import load_dotenv
import os
from sqlalchemy import text
import urllib.parse
from database import db
from utils.image_utils import save_wall_images
import base64

# Initialisation de l'application avant les importations locales
app = Flask(__name__)
load_dotenv()

# Configuration de la base de données et JWT
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 1)
app.config['PAGE_SIZE'] = 10 # Taille des page de l'API

# Initialisation des extensions
db.init_app(app)
jwt = JWTManager(app)

# Import des modèles après l'initialisation de db
from models.db_models import FootHold, Point, Route, Circle, User, Wall, Place
from utils.authentification_utils import register_user, authenticate_user


# Endpoint de test
@app.route('/')
def index():
    return jsonify({'message': 'API Seek a Climb is running'})


# Routes d'authentification
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'userName' not in data or 'password' not in data:
        return jsonify({'error': 'userName et mot de passe requis'}), 400

    user = register_user(data['userName'], data['password'])
    if not user:
        return jsonify({'error': 'userName déjà utilisé'}), 400

    return jsonify({'message': 'Utilisateur créé avec succès'}), 200

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'userName' not in data or 'password' not in data:
        return jsonify({'error': 'userName et mot de passe requis'}), 400

    auth_data = authenticate_user(data['userName'], data['password'])
    if not auth_data:
        return jsonify({'error': 'Identifiants invalides'}), 401

    return jsonify({
        'token': auth_data['token'],
        'user_id': auth_data['user_id']
    }), 200
        

@app.route('/places/search', methods=['GET'])
@jwt_required()
def search_places():
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({'error': 'Le paramètre de recherche est requis'}), 400

        # Recherche des lieux avec un nom similaire
        places = Place.query.filter(
            Place.name.ilike(f'%{search_term}%')
        ).limit(5).all()

        # Conversion en format JSON
        results = [place.toMap() for place in places]
        
        return jsonify(results), 200

    except Exception as e:
        print(f"Erreur lors de la recherche des lieux: {str(e)}")
        return jsonify({'error': 'Erreur lors de la recherche des lieux'}), 500


@app.route('/places/<int:place_id>/routes', methods=['GET'])
@jwt_required()
def get_place_routes(place_id):
    try:
        page = request.args.get('page', 1, type=int)
        wall_id = request.args.get('wall_id', type=int)
        per_page = app.config['PAGE_SIZE']

        place = Place.query.get(place_id)
        if not place:
            return jsonify({'error': 'Lieu non trouvé'}), 404

        # Construction de la requête de base
        query = Route.query.filter(Route.place_id == place_id)

        # Ajouter le filtre wall_id si spécifié
        if wall_id is not None:
            wall = Wall.query.get(wall_id)
            
            if not wall:
                return jsonify({'error': 'Mur non trouvé'}), 404

            query = query.filter(Route.wall_id == wall_id)

        routes = query.paginate(page=page, per_page=per_page)

        # Construction des URLs pour la pagination
        base_url = request.base_url
        params = request.args.copy()
        
        if routes.has_next:
            params['page'] = routes.next_num
            next_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        else:
            next_url = None
            
        if routes.has_prev:
            params['page'] = routes.prev_num
            prev_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        else:
            prev_url = None

        response = {
            'count': routes.total,
            'next': next_url,
            'previous': prev_url,
            'results': [route.toMap() for route in routes.items]
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Erreur lors de la récupération des voies: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération des voies'}), 500

@app.route('/places/<int:place_id>/walls', methods=['GET'])
@jwt_required()
def get_place_walls(place_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = app.config['PAGE_SIZE']

        place = Place.query.get(place_id)
        if not place:
            return jsonify({'error': 'Lieu non trouvé'}), 404

        walls = Wall.query.filter(
            Wall.place_id == place_id
        ).paginate(page=page, per_page=per_page)

        # Construction des URLs pour la pagination
        base_url = request.base_url
        next_url = f"{base_url}?page={walls.next_num}" if walls.has_next else None
        prev_url = f"{base_url}?page={walls.prev_num}" if walls.has_prev else None

        response = {
            'count': walls.total,
            'next': next_url,
            'previous': prev_url,
            'results': [wall.toMap() for wall in walls.items]
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Erreur lors de la récupération des murs: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération des murs'}), 500

@app.route('/routes/create', methods=['POST'])
@jwt_required()
def create_route():
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'grade', 'author_id', 'wall_id', 'place_id', 'isBoulder']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Données manquantes'}), 400
            
        # Création de la route/bloc
        new_route = Route.fromMap(data)
        db.session.add(new_route)
        db.session.flush()  # Pour obtenir l'ID
        
        # Ajout des circles (pour les blocs) ou points (pour les voies)
        if new_route.isBoulder:
            if 'circles' in data and isinstance(data['circles'], list):
                circles = [
                    Circle.fromMap(circle) for circle in data['circles']
                ]
                db.session.bulk_save_objects(circles)
        else:
            if 'points' in data and isinstance(data['points'], list):
                points = [
                    Point.fromMap(point) for point in data['points']
                ]
                db.session.bulk_save_objects(points)
                
        # Ajout des prises de pied
        if 'footholds' in data and isinstance(data['footholds'], list):
            footholds = [
                FootHold.fromMap(foothold) for foothold in data['footholds']
            ]
            db.session.bulk_save_objects(footholds)
            
        db.session.commit()
        
        return jsonify({
            'message': 'Route créée avec succès',
            'route_id': new_route.id
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création de la route: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/walls/create', methods=['POST'])
@jwt_required()
def create_wall():
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['place_id', 'name', 'image', 'thumbnail']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Données manquantes'}), 400
            
        # Récupération du lieu
        place = Place.query.get(data['place_id'])
        if not place:
            return jsonify({'error': 'Lieu non trouvé'}), 404
            
        # Décodage des images depuis base64
        try:
            image_data = base64.b64decode(data['image'])
            thumbnail_data = base64.b64decode(data['thumbnail'])
        except:
            return jsonify({'error': 'Format d\'image invalide'}), 400
            
        # Sauvegarde des images
        filename = save_wall_images(place.name, image_data, thumbnail_data)
        
        # Création du mur dans la base de données
        new_wall = Wall(
            place_id=data['place_id'],
            name=data['name'],
            picture_url=filename
        )
        
        db.session.add(new_wall)
        db.session.commit()
        
        return jsonify({
            'message': 'Mur créé avec succès',
            'wall': new_wall.toMap()
        }), 201
        
    except Exception as e:
        print(f"Erreur lors de la création du mur: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/walls/<int:wall_id>', methods=['GET'])
@jwt_required()
def get_wall(wall_id):
    try:
        wall = Wall.query.get(wall_id)
        if not wall:
            return jsonify({'error': 'Mur non trouvé'}), 404

        return jsonify(wall.toMap()), 200

    except Exception as e:
        print(f"Erreur lors de la récupération du mur: {str(e)}")
        return jsonify({'error': 'Erreur lors de la récupération du mur'}), 500
    

def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("Tables de la base de données créées avec succès")
        except Exception as e:
            print(f"Erreur lors de la création des tables: {e}")
            raise e

if __name__ ==  '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
