from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    Boolean,  
    ForeignKey
    )
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    city = db.Column(db.String(120))
    
    def __init__(self, name, genres, address, city, state, phone, website, facebook_link, image_link, seeking_talent = False, description=""):
        
        self.name = name
        self.facebook_link = facebook_link
        self.website = website
        self.description = description
        self.genres = genres
        self.city = city
        self.state = state
        self.address = address
        self.seeking_talent = seeking_talent
        self.phone = phone
        self.image_link = image_link
        

    def update(self):
        db.session.commit()
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
       
    def delete(self):
        db.session.delete(self)
        db.session.commit()
  
    def long(self):
        return{
            'id' :self.id,
            'name' :self.name,
            'city' : self.city,
            'state' :self.state,
        }
    
    
    def detail(self):
        return{
            'id' :self.id,
            'name' :self.name,
            'genres' : self.genres,
            'phone' :self.phone,
            'website' :self.website,
            'facebook_link':self.facebook_link,
            'address' :self.address,
            'city' :self.city,
            'state':self.state,
            'seeking_talent' :self.seeking_talent,
            'description' :self.description,
            'image-link' :self.image_link
        }
        

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    

    id = Column(Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default=' ')
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __init__(self, name, genres, city, state, phone, image_link, website, facebook_link,
                 seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_description = seeking_description
        self.image_link = image_link
    
    def update(self):
        db.session.commit()
    
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    
    def details(self):
        return{
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'city': self.city,
            'state':self.state,
            'phone': self.phone,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#show model
class Show(db.Model):

    __tablename__ = 'Show'
    id = db.Column(Integer,primary_key=True)
    venue_id = db.Column(Integer, ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(Integer, ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(String(), nullable=False)


    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def detail(self):
        return{
            'venue_id' :self.venue_id,
            'venue_name' :self.venue.name,
            'start_time' :self.start_time,
            'artist_id' :self.artist_id,
            'artist_name' :self.artist.name,
            'artist_image_link' :self.artist.image_link
            
        }

    def venue_details(self):
        return{
            'venue_id' :self.venue_id,
            'venue_name' :self.Venue.name,
            'venue_image_link' :self.Venue.image_link,
            'start_time' :self.start_time
            
        }
    
    
    def artist_details(self):
        return{
            'artist_id' :self.venue_id,
            'start_time' :self.start_time,
            'artist_name' :self.Artist.name,
            'artist_image_link' :self.Artist.image_link,
            }

    