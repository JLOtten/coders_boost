"""Define Create Read Update Delete related functions."""

from model import db, User, Encouragement, UserEncouragement, connect_to_db
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

def save_encouragement(text, language):
    """Save generated encouragements from Open AI API"""

    #TODO: handle this error: psycopg2.errors.UniqueViolation

    #make an encouragement object, from Encouragement class, with attribute text= any given text passes as arg
    encouragement = Encouragement(text=text, language=language)
    db.session.add(encouragement) #add and commit encouragement to the database session
    db.session.commit()

def get_next_encouragement(user, language):
    """Finds the next encouragment to give to a user.
    If an encouragment has not been used, it will show that.
    If all encouragments have been shown, it will show the one
    seen least recently."""

    #get all encouragements in a list: 
    if language is None:
        language = "en"
    encouragements = Encouragement.query.filter_by(language=language).all() #filter encouragements by langugage
     #loop thru encouragements to determine if it has not been seen, if that's true, return it
    for encouragement in encouragements:

        #sql alchemy for a user: get all encouragements seen for that user,
        seen_enc=UserEncouragement.query.filter_by(encouragement_id=encouragement.id, user_id=user.id).all()
        # find encouragements that have been seen (arg, value)
        if len(seen_enc) == 0:
            return encouragement
            
    #make a query for encouragement that was seen least recently
    #how do you order by in sqlalchemy?
    last_seen_user_enc=UserEncouragement.query.filter_by(user_id=user.id).order_by(UserEncouragement.last_viewed_at).all()
    for user_enc in last_seen_user_enc:
        last_seen_enc=Encouragement.query.filter_by(id=user_enc.encouragement_id, language=language).first()
        if last_seen_enc:
            return last_seen_enc
    
    return encouragements[0]

def save_encouragement_seen(user, encouragement):
    """If a given user id has seen a given encouragement_id, then save it."""

    #sql alchemy, create a UserEncouragment instance and save to db
    #similar to OAuth file lines 30-37
    

    query = UserEncouragement.query.filter_by(user_id=user.id, encouragement_id=encouragement.id)
    try:
        encouragement_view=query.one()
        encouragement_view.last_viewed_at = datetime.now()
        db.session.add(encouragement_view)
        db.session.commit()
    except NoResultFound:
        encouragement_view = UserEncouragement(user_id=user.id, encouragement_id=encouragement.id, last_viewed_at=datetime.now())
        db.session.add(encouragement_view)
        db.session.commit()

def save_user_encouragement(user_id, encouragement_id):
    """Saves a favorited encouragement to a user's profile page."""
    #gets seen encouragements by using user_id and encouragement_id's
    query = UserEncouragement.query.filter_by(user_id=user_id, encouragement_id=encouragement_id) #makes general query
    try: #save fav_encouragement to db field favorited_at
        fav_encouragement=query.one() #gets one record from the query
        fav_encouragement.favorited_at = datetime.now() #adds the timestamp
        db.session.add(fav_encouragement)
        db.session.commit()
    except NoResultFound:      #handles case if user tries to favorite encouragement that isn't in db for some reason
        fav_encouragement = UserEncouragement(user_id=user_id, encouragement_id=encouragement_id, favorited_at=datetime.now())
        db.session.add(fav_encouragement)
        db.session.commit()

def delete_user_favorite(user_id, encouragement_id):
    """Removes a favorited user encouragement."""
     #getting one user favorited encouragement, take in the logged in user (current_user_id) so some user can't delete another user's encouragement
    user_encouragement = UserEncouragement.query.filter(UserEncouragement.user_id==user_id, UserEncouragement.encouragement_id==encouragement_id).one()
    #reset favorited_at timestamp to None (to "delete") favorited encouragement
    user_encouragement.favorited_at = None
    db.session.add(user_encouragement)
    db.session.commit()


    