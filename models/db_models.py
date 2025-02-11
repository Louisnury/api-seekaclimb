from database import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, db.Sequence('user_id_seq', start=1, increment=1), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    pp_url = db.Column(db.Text)
    
    # Relations
    routes = db.relationship('Route', backref='author', lazy=True)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            name=data['name'],
            password=data['password'],
            pp_url=data.get('pp_url')
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'pp_url': self.pp_url
        }

class Place(db.Model):
    __tablename__ = 'Place'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    adresse = db.Column(db.Text)
    is_indoor = db.Column(db.Boolean, nullable=False)
    
    # Relations
    routes = db.relationship('Route', backref='place', lazy=True)
    walls = db.relationship('Wall', backref='place', lazy=True)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            name=data['name'],
            lat=data['lat'],
            long=data['long'],
            adresse=data.get('adresse'),
            is_indoor=data['is_indoor']
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'name': self.name,
            'lat': self.lat,
            'long': self.long,
            'adresse': self.adresse,
            'is_indoor': self.is_indoor
        }

class Wall(db.Model):
    __tablename__ = 'Wall'
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('Place.id'), nullable=False)
    picture_url = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    
    # Relations
    routes = db.relationship('Route', backref='wall', lazy=True)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            place_id=data['place_id'],
            picture_url=data['picture_url'],
            name=data['name']
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'place_id': self.place_id,
            'picture_url': self.picture_url,
            'name': self.name
        }

class FootHold(db.Model):
    __tablename__ = 'FootHold'
    route_id = db.Column(db.Integer, db.ForeignKey('Route.id'), primary_key=True)
    hold_id = db.Column(db.Integer, primary_key=True)
    
    __table_args__ = (
        db.PrimaryKeyConstraint('route_id', 'hold_id'),
    )

    @classmethod
    def fromMap(cls, data):
        return cls(
            route_id=data['route_id'],
            hold_id=data['hold_id']
        )
    
    def toMap(self):
        return {
            'route_id': self.route_id,
            'hold_id': self.hold_id
        }

class Point(db.Model):
    __tablename__ = 'Point'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('Route.id'), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            route_id=data['route_id'],
            x=data['x'],
            y=data['y']
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'x': self.x,
            'y': self.y
        }

class Circle(db.Model):
    __tablename__ = 'Circle'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('Route.id'), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, nullable=False)
    hold_type = db.Column(db.Integer, nullable=False)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            route_id=data['route_id'],
            x=data['x'],
            y=data['y'],
            radius=data['radius'],
            hold_type=data['hold_type']
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'x': self.x,
            'y': self.y,
            'radius': self.radius,
            'hold_type': self.hold_type
        }

class Route(db.Model):
    __tablename__ = 'Route'
    
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    wall_id = db.Column(db.Integer, db.ForeignKey('Wall.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('Place.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)
    isBoulder = db.Column(db.Boolean, nullable=False)
    
    # Relations
    circles = db.relationship('Circle', backref='route', lazy=True)
    points = db.relationship('Point', backref='route', lazy=True)
    footholds = db.relationship('FootHold', backref='route', lazy=True)

    @classmethod
    def fromMap(cls, data):
        return cls(
            id=data.get('id'),
            grade=data['grade'],
            author_id=data['author_id'],
            wall_id=data['wall_id'],
            place_id=data['place_id'],
            name=data['name'],
            note=data.get('note'),
            isBoulder=data['isBoulder']
        )
    
    def toMap(self):
        return {
            'id': self.id,
            'grade': self.grade,
            'author_id': self.author_id,
            'wall_id': self.wall_id,
            'place_id': self.place_id,
            'name': self.name,
            'note': self.note,
            'isBoulder': self.isBoulder
        }
