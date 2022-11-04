#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    Boolean, 
    DateTime, 
    ARRAY, 
    ForeignKey
    )
from flask import (
    Flask, 
    render_template, 
    request, Response, 
    flash, redirect, 
    url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from time import gmtime, strftime
from models import db, Venue, Artist, Show
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    locals = []
    venues = Venue.query.all()

    places = Venue.query.distinct(Venue.city, Venue.state).all()

    for place in places:
        locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.shows if dateutil.parser.parse(show.start_time) > datetime.now()])
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
    return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    
    response = {
    "count": len(search_query.all()),
    "data": []
  }
    for search_res in search_query:
        response["data"].append({
      "id": search_res.id,
      "name": search_res.name,
    })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
    venue = Venue.query.get_or_404(venue_id)

    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': dateutil.parser.parse(show.start_time).strftime("%m/%d/%Y, %H:%M")
        }
        if dateutil.parser.parse(show.start_time) <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(venue)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows) 
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    
    form = VenueForm()
#     if not form.validate_on_submit():
#         flash('Make sure you fill form correctly. Check again')
#         return render_template('forms/new_venue.html', form=form)
    
    try:
        venue_data = Venue(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      address=request.form['address'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      website=request.form['website'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      seeking_talent= True if request.form.get('seeking_talent') == 'y' else False,
      description=request.form['seeking_description']
    )
        Venue.insert(venue_data)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' was not listed!')
        
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE', 'GET', 'POST'])
def delete_venue(venue_id):
    
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Selected venue has been successfully DELETED')
        return render_template('pages/home.html')
    except:
        db.session.rollback() 
    finally:
        db.session.close()

    flash(' X Venue could not be deleted. Something went wrong. X')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    artist_query = Artist.query.all()
    return render_template('pages/artists.html', artists=artist_query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
    search_param = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
        
    response = {
    "count":len(search_param),
    "data": []
  }
    
    for parameter in search_param:
        response["data"].append({
      "id": parameter.id,
      "name": parameter.name,
        })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
    artist = Artist.query.get_or_404(artist_id)

    past_shows = []
    upcoming_shows = []

    for show in artist.shows:
        temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': dateutil.parser.parse(show.start_time).strftime("%m/%d/%Y, %H:%M")
        }
    
        if dateutil.parser.parse(show.start_time) <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(artist)

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)



#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    
    
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    if not artist:
        flash('Artist does not exist')
        return render_template('pages/home.html')
    
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)
#     return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
    form = ArtistForm(request.form)
    artist_data = Artist.query.get(artist_id)
    if artist_data:
        seeking_venue = False
        seeking_description = ''
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        setattr(artist_data, 'name', request.form['name'])
        setattr(artist_data, 'genres', request.form.getlist('genres'))
        setattr(artist_data, 'city', request.form['city'])
        setattr(artist_data, 'state', request.form['state'])
        setattr(artist_data, 'phone', request.form['phone'])
        setattr(artist_data, 'website', request.form['website'])
        setattr(artist_data, 'facebook_link', request.form['facebook_link'])
        setattr (artist_data, 'image_link', request.form['image_link'])
        setattr(artist_data, 'seeking_description', seeking_description)
        setattr(artist_data, 'seeking_venue', seeking_venue)
        Artist.update(artist_data)
        return redirect(url_for('show_artist', artist_id=artist_id))     
    return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venue_details = Venue.detail(venue_query)
        print(venue_details.keys())
        form.name.data = venue_details["name"]
        form.genres.data = venue_details["genres"]
        form.address.data = venue_details["address"]
        form.city.data = venue_details["city"]
        form.state.data = venue_details["state"]
        form.phone.data = venue_details["phone"]
        form.website.data = venue_details["website"]
        form.facebook_link.data = venue_details["facebook_link"]
        form.seeking_talent.data = venue_details["seeking_talent"]
        form.seeking_description.data = venue_details["description"]
        form.image_link.data = venue_details["image-link"]
        return render_template('forms/edit_venue.html', form=form, venue=venue_details)
    return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue_data = Venue.query.get(venue_id)
    if venue_data: 
        seeking_talent = False
        seeking_description = ''
        if 'seeking_talent' in request.form:
            seeking_talent = request.form['seeking_talent'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        setattr(venue_data, 'name', request.form['name'])
        setattr(venue_data, 'genres', request.form.getlist('genres'))
        setattr(venue_data, 'address', request.form['address'])
        setattr(venue_data, 'city', request.form['city'])
        setattr(venue_data, 'state', request.form['state'])
        setattr(venue_data, 'phone', request.form['phone'])
        setattr(venue_data, 'website', request.form['website'])
        setattr(venue_data, 'facebook_link', request.form['facebook_link'])
        setattr(venue_data, 'image_link', request.form['image_link'])
        setattr(venue_data, 'seeking_description', seeking_description)
        setattr(venue_data, 'seeking_talent', seeking_talent)
        Venue.update(venue_data)
        return redirect(url_for('show_venue', venue_id=venue_id))
    return render_template('errors/404.html'), 404

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    
    form = ArtistForm()
#     if not form.validate_on_submit():
#         flash('Make sure you fill the form correctly. Check Again')
#         return render_template('forms/new_artist.html', form=form)
    
    try:
        new_artist = Artist(
            name = request.form['name'],
            genres = request.form.getlist('genres'),
            city = request.form['city'],
            state= request.form['state'],
            phone = request.form['phone'],
            website = request.form['website'],
            image_link = request.form['image_link'],
            facebook_link = request.form['facebook_link'],
            seeking_venue = True if request.form.get('seeking_venue') == 'y' else False,
            seeking_description = request.form['seeking_description']
        )
        Artist.insert(new_artist)
        flash('Artist ' + request.form['name'] + ' was listed successfully!')
    except SQLAlchemyError as e:
        flash('Something went wrong. Artist ' + request.form['name'] + 'could not be added to list. ')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
    show_query = Show.query.options(db.joinedload(Show.venue), db.joinedload(Show.artist)).all()
    data = list(map(Show.detail, show_query))
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    
    form = ShowForm()
#     if not form.validate_on_submit():
#         flash('Make sure you fill the form correctly. Check again')
#         return render_template('forms/new_show.html', form=form)
    
    try:
        new_show = Show(
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        start_time=request.form['start_time'],
        )
        Show.insert(new_show)
        flash('Show was successfully listed!')
    except SQLAlchemyError as e:
        flash('Show not listed. Check id')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
