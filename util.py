import urllib
from google.appengine.api import users
from django.template.defaultfilters import pluralize

import facebook_util


"""Returns users.get_current_user() if not None, or a faked User based on the
user's Facebook account if the user has one, or None.
"""
def get_current_user():

    appengine_user = users.get_current_user()

    if appengine_user is not None:
        return appengine_user

    facebook_user = facebook_util.get_current_facebook_user()

    if facebook_user is not None:
        return facebook_user   

    return None

def get_nickname_for(user):
    if facebook_util.is_facebook_email(user.email()):
        return facebook_util.get_facebook_nickname(user)
    else:
        return user.nickname()

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)

def minutes_between(dt1, dt2):
    timespan = dt2 - dt1
    return float(timespan.seconds + (timespan.days * 24 * 3600)) / 60.0

def seconds_to_time_string(seconds_init):

    seconds = seconds_init

    hours = seconds / 3600
    seconds -= hours * 3600

    minutes = seconds / 60
    seconds -= minutes * 60

    if hours and minutes and seconds:
        return "%d hour%s, %d minute%s, and %d second%s" % (hours, pluralize(hours), minutes, pluralize(minutes), seconds, pluralize(seconds))
    elif hours and minutes:
        return "%d hour%s and %d minute%s" % (hours, pluralize(hours), minutes, pluralize(minutes))
    elif hours:
        return "%d hour%s" % (hours, pluralize(hours))
    elif minutes and seconds:
        return "%d minute%s and %d second%s" % (minutes, pluralize(minutes), seconds, pluralize(seconds))
    elif minutes:
        return "%d minute%s" % (minutes, pluralize(minutes))
    else:
        return "%d second%s" % (seconds, pluralize(seconds))

def thousands_separated_number(x):
    # See http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


