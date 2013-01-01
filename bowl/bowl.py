# This web app runs a contest for college football bowl games.
#
# Each bowl game has a name and two teams.  We associate unique
# 2-letter id's to each game, and 2-4 letter id's to each team.  For
# example:
#
#   New Mexico Bowl (NM) -- Nevada (NEV) vs Arizona (ARIZ)
#   Russell Athletic Bowl (RA) -- Rutgers (RUTG) vs Virginia Tech (VT)
#
# Each user can vote for which team will win each bowl.  These choices
# are stored hierarchically like so:
#
#   Player('alice')
#     Choice(bowl='NM', team='NEV')
#     Choice(bowl='RA', team='RUTG')
#   Player('bob')
#     Choice(bowl='NM', team='NEV')
#     Choice(bowl='RA', team='VT') 
#
# The actual game outcomes can be set by the admin user, and these are
# stored under a singleton object:
#
#   Winners('singleton')
#     Choice(bowl='NM', team='ARIZ')
#     Choice(bowl='RA', team='VT')
#
# The users make their selections at /player/choose, which then posts
# to /player/save when the user clicks a team.
#
# Similarly, game outcomes go through /admin/choose and /admin/save.
#
# In addition, there is an overall summary at /public/scoreboard,
# viewable by anyone (including non-logged-in visitors).

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
    ('2012 Dec 20  8:00 pm', 'PA', 'BYU',  'SDSU', 'Poinsettia', 'BYU', 'San Diego St'),
    ('2012 Dec 21  7:30 pm', 'BB', 'BALL', 'UCF',  "Beef 'O' Brady's", 'Ball St', 'UCF'),
    ('2012 Dec 22 12:00 pm', 'NO', 'ECU',  'ULL',  'New Orleans', 'East Carolina', 'LA-Lafayette'),
    ('2012 Dec 22  3:30 pm', 'MA', 'WASH', 'BSU',  'Maaco', 'Washington', 'Boise St'),
    ('2012 Dec 24  8:00 pm', 'HI', 'FRES', 'SMU',  "Hawai'i", 'Fresno St', 'SMU'),
    ('2012 Dec 26  7:30 pm', 'LC', 'WKU',  'CMU',  'Little Caesars Pizza', 'W Kentucky', 'Cent Michigan'),
    ('2012 Dec 27  3:00 pm', 'MI', 'SJSU', 'BGSU', 'Military', 'San Jose St', 'Bowling Green'),
    ('2012 Dec 27  6:30 pm', 'BK', 'CIN',  'DUKE', 'Belk', 'Cincinnati', 'Duke'),
    ('2012 Dec 27  9:45 pm', 'HO', 'BAY',  'UCLA', 'Holiday', 'Baylor', 'UCLA'),
    ('2012 Dec 28  2:00 pm', 'IN', 'OHIO', 'ULM',  'Independence', 'Ohio', 'LA-Monroe'),
    ('2012 Dec 28  5:30 pm', 'RA', 'RUTG', 'VT',   'Russell Athletic', 'Rutgers', 'Virginia Tech'),
    ('2012 Dec 28  9:00 pm', 'ME', 'MINN', 'TTU',  'Meineke Car Care', 'Minnesota', 'Texas Tech'),
    ('2012 Dec 29 11:45 am', 'AF', 'RICE', 'AFA',  'Armed Forces', 'Rice', 'Air Force'),
    ('2012 Dec 29  3:15 pm', 'PS', 'WVU',  'SYR',  'Pinstripe', 'West Virginia', 'Syracuse'),
    ('2012 Dec 29  4:00 pm', 'FH', 'NAVY', 'ASU',  'Fight Hunger', 'Navy', 'Arizona St'),
    ('2012 Dec 29  6:45 pm', 'AL', 'TEX',  'ORST', 'Alamo', 'Texas', 'Oregon St'),
    ('2012 Dec 29 10:15 pm', 'BW', 'TCU',  'MSU',  'Buffalo Wild Wings', 'TCU', 'Michigan St'),
    ('2012 Dec 31 12:00 pm', 'MU', 'NCST', 'VAN',  'Music City', 'NC State', 'Vanderbilt'),
    ('2012 Dec 31  2:00 pm', 'SN', 'USC',  'GT',   'Sun', 'USC', 'Georgia Tech'),
    ('2012 Dec 31  3:30 pm', 'LY', 'ISU',  'TLSA', 'Liberty', 'Iowa St', 'Tulsa'),
    ('2012 Dec 31  7:30 pm', 'CK', 'LSU',  'CLEM', 'Chick-fil-A', 'LSU', 'Clemson'),
    ('2013 Jan  1 12:00 pm', 'GA', 'MSST', 'NW',   'Gator', 'Miss. St', 'Northwestern'),
    ('2013 Jan  1 12:00 pm', 'HD', 'PUR',  'OKST', 'Heart of Dallas', 'Purdue', 'Oklahoma St'),
    ('2013 Jan  1  1:00 pm', 'OU', 'SCAR', 'MICH', 'Outback', 'South Carolina', 'Michigan'),
    ('2013 Jan  1  1:00 pm', 'C1', 'UGA',  'NEB',  'Capital One', 'Georgia', 'Nebraska'),
    ('2013 Jan  1  5:00 pm', 'RO', 'WIS',  'STAN', 'Rose', 'Wisconsin', 'Stanford'),
    ('2013 Jan  1  8:30 pm', 'OR', 'NIU',  'FSU',  'Orange', 'N Illinois', 'Florida St'),
    ('2013 Jan  2  8:30 pm', 'SG', 'LOU',  'FLA',  'Sugar', 'Louisville', 'Florida'),
    ('2013 Jan  3  8:30 pm', 'FA', 'ORE',  'KSU',  'Fiesta', 'Oregon', 'Kansas St'),
    ('2013 Jan  4  8:00 pm', 'CN', 'TA&M', 'OKLA', 'Cotton', 'Texas A&M', 'Oklahoma'),
    ('2013 Jan  5  1:00 pm', 'CS', 'PITT', 'MISS', 'Compass', 'Pittsburgh', 'Ole Miss'),
    ('2013 Jan  6  9:00 pm', 'GO', 'KENT', 'ARST', 'GoDaddy.com', 'Kent St', 'Arkansas St'),
    ('2013 Jan  7  8:30 pm', 'NC', 'ND',   'ALA',  'BCS National Championship', 'Notre Dame', 'Alabama'),
    ]

class Winners(db.Model):
    """Parent entity for Choice entities representing bowl outcomes.
    NB: We only create one such entity, and its key name is 'singleton'"""

class Player(db.Model):
    """Represents a user who is guessing bowl results."""
    user = db.UserProperty(required=True)
    pct_correct = db.FloatProperty()

class Choice(db.Model):
    """The team chosen to win a given bowl.
    Each Choice has a Player parent, or has the Winners singleton as parent."""
    bowl = db.StringProperty(required=True)
    team = db.StringProperty(required=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        logout = None
        is_admin = False
        user = users.get_current_user()
        if user:
            logout = users.create_logout_url('/')
            if users.is_current_user_admin():
                is_admin = True
        tmpl = jinja_environment.get_template('index.html')
        self.response.out.write(tmpl.render(is_admin=is_admin, logout=logout))

class Choose(webapp2.RequestHandler):
    def choose(self, parent, greeting, is_admin):
        choice_query = Choice.all()
        choice_query.ancestor(parent)
        choices = dict((c.bowl, c.team) for c in choice_query.run())
        tmpl = jinja_environment.get_template('choose.html')
        self.response.out.write(tmpl.render(
                greeting=greeting, bowls=BOWLS, choices=choices,
                is_admin=is_admin))

class PlayerChoose(Choose):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.response.out.write('<html><body>Login required</body></html>')
            return
        parent = Player.get_or_insert(user.user_id(), user=user)
        self.choose(parent=parent,
                    greeting='Welcome %s !' % user.nickname(),
                    is_admin=False)

class AdminChoose(Choose):
    def get(self):
        parent = Winners.get_or_insert('singleton')
        self.choose(parent=parent,
                    greeting='ADMIN PAGE: Select winners',
                    is_admin=True)

class Save(webapp2.RequestHandler):
    def save(self, user):
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
                if user is not None:
                    # UTC is 5 hours ahead of EST
                    utc_kickoff = (
                        datetime.datetime.strptime(d, '%Y %b %d %I:%M %p') +
                        datetime.timedelta(hours=5))
                    if datetime.datetime.utcnow() > utc_kickoff:
                        self.response.out.write('Game already started!')
                        return
                break
        else:
            self.response.out.write('Invalid bowl: %s' % cgi.escape(bowl))
            return

        # Store or delete a choice
        if team:
            if user is None:
                parent = Winners.get_or_insert('singleton')
            else:
                parent = Player.get_or_insert(user.user_id(), user=user)
            Choice(parent=parent, key_name=bowl, bowl=bowl, team=team).put()
        else:
            if user is None:
                key = db.Key.from_path('Winners', 'singleton', 'Choice', bowl)
            else:
                key = db.Key.from_path('Player', user.user_id(), 'Choice', bowl)
            db.delete(key)
        self.response.out.write('Saved')

class PlayerSave(Save):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        user = users.get_current_user()
        if not user:
            self.response.out.write('Login required')
            return
        self.save(user)

class AdminSave(Save):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.save(None)

def query_winners():
    """Returns a dict mapping each bowl id to the winning team's id."""
    parent = Winners.get_or_insert('singleton')
    q = Choice.all()
    q.ancestor(parent)
    return dict((c.bowl, c.team) for c in q.run())

class AdminUpdate(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        winners = query_winners()

        # Update all the players
        player_query = db.GqlQuery('SELECT * FROM Player')
        players = []
        for player in player_query.run():
            total = 0
            correct = 0
            choice_query = Choice.all()
            choice_query.ancestor(player)
            for c in choice_query.run():
                if c.bowl in winners:
                    total += 1
                    if  winners[c.bowl] == c.team:
                        correct += 1
            if total == 0:
                player.pct_correct = 0.0
            else:
                player.pct_correct = float(correct) / total
            player.put()
        self.response.out.write('OK')

def started_bowls():
    # TODO: Represent bowls using a dict/class instead of a tuple.
    started = set()
    utc_now = datetime.datetime.utcnow()
    for d, b, _, _, _, _, _ in BOWLS:
        # UTC is 5 hours ahead of EST
        utc_kickoff = (datetime.datetime.strptime(d, '%Y %b %d %I:%M %p')
                       + datetime.timedelta(hours=5))
        if utc_kickoff < utc_now:
            started.add(b)
    return started

class Scoreboard(webapp2.RequestHandler):
    def get(self):
        winners = query_winners()

        # Look up all the players
        player_query = db.GqlQuery('SELECT * FROM Player '
                                   'ORDER BY pct_correct DESC')

        started = started_bowls()
        players = []
        for player in player_query.run():
            choice_query = Choice.all()
            choice_query.ancestor(player)
            choices = dict((c.bowl, c.team) for c in choice_query.run()
                           if c.bowl in started)
            players.append((player, choices))
        tmpl = jinja_environment.get_template('scoreboard.html')
        self.response.out.write(tmpl.render(
                bowls=BOWLS, players=players, winners=winners))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/admin/choose', AdminChoose),
                               ('/admin/save', AdminSave),
                               ('/admin/update', AdminUpdate),
                               ('/player/choose', PlayerChoose),
                               ('/player/save', PlayerSave),
                               ('/public/scoreboard', Scoreboard)],
                              debug=True)
