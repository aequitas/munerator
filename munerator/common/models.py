__all__ = ['Players', 'Games', 'Votes']

from mongoengine import (BooleanField, Document, IntField, DictField,
                         ListField, ReferenceField, StringField, URLField)


class Players(Document):
    guid = StringField()
    name = StringField()
    names = ListField(StringField())
    online = BooleanField()
    score = IntField()
    team = StringField()
    team_id = IntField()
    skill = StringField()
    address = StringField()
    bot = BooleanField()
    headmodel = StringField()


class Gamemaps(Document):
    name = StringField()
    levelshot = URLField()
    images = ListField(URLField())
    gametypes = ListField(IntField())


class Votes(Document):
    game = ReferenceField('Games')
    player = ReferenceField('Players')
    vote = IntField()


class Games(Document):
    timestamp = StringField()
    mapname = StringField()
    gamemap = ReferenceField(Gamemaps)
    gametype = IntField()
    players = ListField(ReferenceField('Players'))
    votes = ListField(ReferenceField('Votes'))
    state = StringField()
    start = StringField()
    stop = StringField()
    num_players = IntField()
    current = BooleanField()
    options = DictField()
