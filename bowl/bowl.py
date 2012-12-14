import cgi
import datetime
import jinja2
import os
import time
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

BOWLS = [
    ('NM', 'NEV',  'ARIZ', 'New Mexico', 'Nevada', 'Arizona'),
    ('IP', 'TOL',  'USU',  'Idaho Potato', 'Toledo', 'Utah St'),
    ('PA', 'BYU',  'SDSU', 'Poinsettia', 'BYU', 'SDSU'),
    ('BB', 'UCF',  'BALL', "Beef 'O' Brady's", 'C Florida', 'Ball St'),
    ('NO', 'ECU',  'ULL',  'New Orleans', 'E Carolina', 'La Lafayette'),
    ('MA', 'WASH', 'BSU',  'Maaco', 'Washington', 'Boise St'),
    ('HI', 'FRES', 'SMU',  "Hawai'i", 'Fresno St', 'SMU'),
    ('LC', 'WKU',  'CMU',  'Little Caesars Pizza', 'W Kentucky', 'C Michigan'),
    ('MI', 'SJSU', 'BGSU', 'Military', 'San Jose St', 'BGU'),
    ('BK', 'CIN',  'DUKE', 'Belk', 'Cincy', 'Duke'),
    ('HO', 'BAY',  'UCLA', 'Holiday', 'Baylor', 'UCLA'),
    ('IN', 'OHIO', 'ULM',  'Independence', 'Ohio', 'UL-Monroe'),
    ('RA', 'RUTG', 'VT',   'Russell Athletic', 'Rutgers', 'Virginia Tech'),
    ('ME', 'MINN', 'TTU',  'Meneike Car Care', 'Minnesota', 'Texas Tech'),
    ('AF', 'RICE', 'AFA',  'Armed Forces', 'Rice', 'Air Force'),
    ('PS', 'WVU',  'SYR',  'Pinstripe', 'W Virginia', 'Syracuse'),
    ('FH', 'NAVY', 'ASU',  'Fight Hunger', 'Navy', 'Arizona St'),
    ('AL', 'TEX',  'ORST', 'Alamo', 'Texas', 'Oregon St'),
    ('BW', 'TCU',  'MSU',  'Buffalo Wild Wings', 'TCU', 'Mich St'),
    ('MU', 'NCST', 'VAN',  'Music City', 'NC State', 'Vanderbilt'),
    ('SN', 'USC',  'GT',   'Sun', 'USC', 'Ga Tech'),
    ('LY', 'ISU',  'TLSA', 'Liberty', 'Iowa St', 'Tulsa'),
    ('CK', 'LSU',  'CLEM', 'Chick-fil-A', 'LSU', 'Clemson'),
    ('GA', 'MSST', 'NW',   'Gator', 'Miss St', "N'western"),
    ('HD', 'PUR',  'OKST', 'Heart of Dallas', 'Purdue', 'Oklahoma St'),
    ('OU', 'SCAR', 'MICH', 'Outback', 'S Carolina', 'Michigan'),
    ('C1', 'UGA',  'NEB',  'Capital One', 'Georgia', 'Nebraska'),
    ('RO', 'WIS',  'STAN', 'Rose', 'Wisconsin', 'Stanford'),
    ('OR', 'NIU',  'FSU',  'Orange', 'N Illinois', 'Florida St'),
    ('SG', 'LOU',  'FLA',  'Sugar', 'Louisville', 'Florida'),
    ('FA', 'ORE',  'KSU',  'Fiesta', 'Oregon', 'Kansas St'),
    ('CN', 'TA&M', 'OKLA', 'Cotton', 'Texas A&M', 'Oklahoma'),
    ('CS', 'PITT', 'MISS', 'Compass', 'Pittsburgh', 'Ole Miss'),
    ('GO', 'KENT', 'ARST', 'GoDaddy.com', 'Kent St', 'Arkansas St'),
    ('NC', 'ALA',  'ND',   'BCS National Championship', 'Alabama', 'N Dame'),
    ]

class Player(db.Model):
    user = db.UserProperty(required=True)

class Choice(db.Model):
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
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        user = users.get_current_user()
        if not user:
            self.response.out.write('Login required')
            return
        bowl = self.request.get('bowl')
        team = self.request.get('team')

        # Verify inputs
        for b, t1, t2, _, _, _ in BOWLS:
            if bowl == b:
                if team and team not in [t1, t2]:
                    self.response.out.write(
                        'Invalid team for bowl %s: %s' %
                        (cgi.escape(bowl), cgi.escape(team)))
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

class Scoreboard(webapp2.RequestHandler):
    def get(self):
        next_cursor = self.request.get('next')
        player_query = db.GqlQuery('SELECT * FROM Player '
                                   'ORDER BY user '
                                   'LIMIT 10')
        # TODO: Catch bad cursor here?
        if next_cursor:
            player_query.with_cursor(next_cursor)
        players = []
        for player in player_query.run():
            choice_query = Choice.all()
            choice_query.ancestor(player)
            choices = dict((c.bowl, c.team) for c in choice_query.run())
            players.append((player, choices))
        next_cursor = player_query.cursor()
        tmpl = jinja_environment.get_template('scoreboard.html')
        self.response.out.write(tmpl.render(
                bowls=BOWLS, players=players, next=next_cursor))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/player/choose', Choose),
                               ('/player/save', Save),
#                               ('/public/scoreboard', Scoreboard)],
                               ],
                              debug=True)
