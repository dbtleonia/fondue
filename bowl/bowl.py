# TODO: Write comments.

import cgi
import datetime
import os
import time
import urllib
import webapp2

import jinja2  # configured in app.yaml

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# NB: All times Eastern.
BOWLS = [
    ('2012 Dec 15  1:00 pm', 'NM', 'NEV',  'ARIZ', 'New Mexico', 'Nevada', 'Arizona'),
    ('2012 Dec 15  4:30 pm', 'IP', 'TOL',  'USU',  'Idaho Potato', 'Toledo', 'Utah St'),
    ('2012 Dec 20  8:00 pm', 'PA', 'BYU',  'SDSU', 'Poinsettia', 'BYU', 'SDSU'),
    ('2012 Dec 21  7:30 pm', 'BB', 'UCF',  'BALL', "Beef 'O' Brady's", 'C Florida', 'Ball St'),
    ('2012 Dec 22 12:00 pm', 'NO', 'ECU',  'ULL',  'New Orleans', 'E Carolina', 'La Lafayette'),
    ('2012 Dec 22  3:30 pm', 'MA', 'WASH', 'BSU',  'Maaco', 'Washington', 'Boise St'),
    ('2012 Dec 24  8:00 pm', 'HI', 'FRES', 'SMU',  "Hawai'i", 'Fresno St', 'SMU'),
    ('2012 Dec 26  7:30 pm', 'LC', 'WKU',  'CMU',  'Little Caesars Pizza', 'W Kentucky', 'C Michigan'),
    ('2012 Dec 27  3:00 pm', 'MI', 'SJSU', 'BGSU', 'Military', 'San Jose St', 'BGU'),
    ('2012 Dec 27  6:30 pm', 'BK', 'CIN',  'DUKE', 'Belk', 'Cincy', 'Duke'),
    ('2012 Dec 27  9:45 pm', 'HO', 'BAY',  'UCLA', 'Holiday', 'Baylor', 'UCLA'),
    ('2012 Dec 28  2:00 pm', 'IN', 'OHIO', 'ULM',  'Independence', 'Ohio', 'UL-Monroe'),
    ('2012 Dec 28  5:30 pm', 'RA', 'RUTG', 'VT',   'Russell Athletic', 'Rutgers', 'Virginia Tech'),
    ('2012 Dec 28  9:00 pm', 'ME', 'MINN', 'TTU',  'Meneike Car Care', 'Minnesota', 'Texas Tech'),
    ('2012 Dec 29 11:45 am', 'AF', 'RICE', 'AFA',  'Armed Forces', 'Rice', 'Air Force'),
    ('2012 Dec 29  3:15 pm', 'PS', 'WVU',  'SYR',  'Pinstripe', 'W Virginia', 'Syracuse'),
    ('2012 Dec 29  4:00 pm', 'FH', 'NAVY', 'ASU',  'Fight Hunger', 'Navy', 'Arizona St'),
    ('2012 Dec 29  6:45 pm', 'AL', 'TEX',  'ORST', 'Alamo', 'Texas', 'Oregon St'),
    ('2012 Dec 29 10:15 pm', 'BW', 'TCU',  'MSU',  'Buffalo Wild Wings', 'TCU', 'Mich St'),
    ('2012 Dec 31 12:00 pm', 'MU', 'NCST', 'VAN',  'Music City', 'NC State', 'Vanderbilt'),
    ('2012 Dec 31  2:00 pm', 'SN', 'USC',  'GT',   'Sun', 'USC', 'Ga Tech'),
    ('2012 Dec 31  3:30 pm', 'LY', 'ISU',  'TLSA', 'Liberty', 'Iowa St', 'Tulsa'),
    ('2012 Dec 31  7:30 pm', 'CK', 'LSU',  'CLEM', 'Chick-fil-A', 'LSU', 'Clemson'),
    ('2013 Jan  1 12:00 pm', 'GA', 'MSST', 'NW',   'Gator', 'Miss St', "N'western"),
    ('2013 Jan  1 12:00 pm', 'HD', 'PUR',  'OKST', 'Heart of Dallas', 'Purdue', 'Oklahoma St'),
    ('2013 Jan  1  1:00 pm', 'OU', 'SCAR', 'MICH', 'Outback', 'S Carolina', 'Michigan'),
    ('2013 Jan  1  1:00 pm', 'C1', 'UGA',  'NEB',  'Capital One', 'Georgia', 'Nebraska'),
    ('2013 Jan  1  5:00 pm', 'RO', 'WIS',  'STAN', 'Rose', 'Wisconsin', 'Stanford'),
    ('2013 Jan  1  8:30 pm', 'OR', 'NIU',  'FSU',  'Orange', 'N Illinois', 'Florida St'),
    ('2013 Jan  2  8:30 pm', 'SG', 'LOU',  'FLA',  'Sugar', 'Louisville', 'Florida'),
    ('2013 Jan  3  8:30 pm', 'FA', 'ORE',  'KSU',  'Fiesta', 'Oregon', 'Kansas St'),
    ('2013 Jan  4  8:00 pm', 'CN', 'TA&M', 'OKLA', 'Cotton', 'Texas A&M', 'Oklahoma'),
    ('2013 Jan  5  1:00 pm', 'CS', 'PITT', 'MISS', 'Compass', 'Pittsburgh', 'Ole Miss'),
    ('2013 Jan  6  9:00 pm', 'GO', 'KENT', 'ARST', 'GoDaddy.com', 'Kent St', 'Arkansas St'),
    ('2013 Jan  7  8:30 pm', 'NC', 'ALA',  'ND',   'BCS National Championship', 'Alabama', 'N Dame'),
    ]

class Player(db.Model):
    """Represents a user who is guessing bowl results."""
    user = db.UserProperty(required=True)

class Choice(db.Model):
    """The team chosen to win a given bowl.  Each Choice has a Player parent."""
    bowl = db.StringProperty(required=True)
    team = db.StringProperty(required=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        logout = None
        user = users.get_current_user()
        if user:
            logout = users.create_logout_url('/')
        tmpl = jinja_environment.get_template('index.html')
        self.response.out.write(tmpl.render(logout=logout))

class Choose(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.response.out.write('<html><body>Login required</body></html>')
            return
        player = Player.get_or_insert(user.user_id(), user=user)
        choice_query = Choice.all()
        choice_query.ancestor(player)
        choices = dict((c.bowl, c.team) for c in choice_query.run())
        tmpl = jinja_environment.get_template('choose.html')
        self.response.out.write(tmpl.render(
                bowls=BOWLS, choices=choices, user=user))

class Save(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        user = users.get_current_user()
        if not user:
            self.response.out.write('Login required')
            return
        bowl = self.request.get('bowl')
        team = self.request.get('team')

        # Verify inputs
        for d, b, t1, t2, _, _, _ in BOWLS:
            if bowl == b:
                if team and team not in [t1, t2]:
                    self.response.out.write(
                        'Invalid team for bowl %s: %s' %
                        (cgi.escape(bowl), cgi.escape(team)))
                    return
                # UTC is 5 hours ahead of EST
                utc_kickoff = (datetime.datetime.strptime(d, '%Y %b %d %I:%M %p')
                               + datetime.timedelta(hours=5))
                if datetime.datetime.utcnow() > utc_kickoff:
                    self.response.out.write('Game already started!')
                    return
                break
        else:
            self.response.out.write('Invalid bowl: %s' % cgi.escape(bowl))
            return

        # Store or delete a choice
        if team:
            player = Player.get_or_insert(user.user_id(), user=user)
            Choice(parent=player, key_name=bowl, bowl=bowl, team=team).put()
        else:
            db.delete(db.Key.from_path('Player', user.user_id(),
                                       'Choice', bowl))
        self.response.out.write('Saved')

def completed_bowls():
    # TODO: Represent bowls using a dict/class instead of a tuple.
    completed = set()
    utc_now = datetime.datetime.utcnow()
    for d, b, _, _, _, _, _ in BOWLS:
        # UTC is 5 hours ahead of EST
        utc_kickoff = (datetime.datetime.strptime(d, '%Y %b %d %I:%M %p')
                       + datetime.timedelta(hours=5))
        if utc_kickoff < utc_now:
            completed.add(b)
    return completed

class Scoreboard(webapp2.RequestHandler):
    def get(self):
        next_cursor = self.request.get('next')
        player_query = db.GqlQuery('SELECT * FROM Player '
                                   'ORDER BY user '
                                   'LIMIT 10')
        # TODO: Catch bad cursor here?
        if next_cursor:
            player_query.with_cursor(next_cursor)

        completed = completed_bowls()
        players = []
        for player in player_query.run():
            choice_query = Choice.all()
            choice_query.ancestor(player)
            choices = dict((c.bowl, c.team) for c in choice_query.run()
                           if c.bowl in completed)
            players.append((player, choices))
        next_cursor = player_query.cursor()
        tmpl = jinja_environment.get_template('scoreboard.html')
        self.response.out.write(tmpl.render(
                bowls=BOWLS, players=players, next=next_cursor))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/player/choose', Choose),
                               ('/player/save', Save),
                               ('/public/scoreboard', Scoreboard)],
                              debug=True)
