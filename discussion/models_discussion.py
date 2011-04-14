#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import memcache

from app import App
from nicknames import get_nickname_for

class FeedbackType:
    Question="question"
    Answer="answer"
    Comment="comment"

    @staticmethod
    def is_valid(type):
        return (type == FeedbackType.Question or 
                type == FeedbackType.Answer or 
                type == FeedbackType.Comment)

class FeedbackFlag:

    # 2 or more flags immediately hides feedback
    HIDE_LIMIT = 2

    Inappropriate="inappropriate"
    LowQuality="lowquality"
    DoesNotBelong="doesnotbelong"
    Spam="spam"

    @staticmethod
    def is_valid(flag):
        return (flag == FeedbackFlag.Inappropriate or 
                flag == FeedbackFlag.LowQuality or 
                flag == FeedbackFlag.DoesNotBelong or 
                flag == FeedbackFlag.Spam)

class Feedback(db.Model):
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    targets = db.ListProperty(db.Key)
    types = db.StringListProperty()
    is_flagged = db.BooleanProperty(default=False)
    is_hidden_by_flags = db.BooleanProperty(default=False)
    flags = db.StringListProperty(default=None)
    flagged_by = db.StringListProperty(default=None)

    @staticmethod
    def memcache_key_for_video(video):
        return "video_feedback_%s" % video.key()

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        self.children_cache = [] # For caching each question's answers during render

    def put(self):
        memcache.delete(Feedback.memcache_key_for_video(self.first_target()), namespace=App.version)
        db.Model.put(self)

    def is_type(self, type):
        return type in self.types

    def parent_key(self):
        if self.targets:
            return self.targets[-1]
        return None

    def parent(self):
        return db.get(self.parent_key())

    def children_keys(self):
        keys = db.Query(Feedback, keys_only=True)
        keys.filter("targets = ", self.key())
        return keys

    def first_target(self):
        if self.targets:
            return db.get(self.targets[0])
        return None

    def author_nickname(self):
        return get_nickname_for(self.author)

    def add_flag_by(self, flag_type, user):
        if user.email() in self.flagged_by:
            return False

        self.flags.append(flag_type)
        self.flagged_by.append(user.email())
        self.recalculate_flagged()
        return True

    def clear_flags(self):
        self.flags = []
        self.flagged_by = []
        self.recalculate_flagged()

    def recalculate_flagged(self):
        self.is_flagged = len(self.flags or []) > 0
        self.is_hidden_by_flags = len(self.flags or []) >= FeedbackFlag.HIDE_LIMIT

class FeedbackNotification(db.Model):
    feedback = db.ReferenceProperty(Feedback)
    user = db.UserProperty()
