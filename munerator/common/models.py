__all__ = ['Players', 'Games', 'Votes']

from mongoengine import (BooleanField, Document, IntField, DictField, DateTimeField,
                         ListField, ReferenceField, StringField, URLField, FloatField)


class Players(Document):
    guid = StringField()
    guids = ListField(StringField())
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
    last_seen = DateTimeField()

    # fields allowed to be updated by context info
    update_fields = ['name', 'online', 'score', 'team', 'team_id', 'skill', 'address', 'bot', 'headmodel']


class Gamemaps(Document):
    name = StringField()
    levelshot = URLField()
    images = ListField(URLField())
    gametypes = ListField(IntField())
    min_players = IntField(default=2)
    max_players = IntField(default=12)
    times_played = IntField(default=0)
    last_played = DateTimeField()


class Votes(Document):
    game = ReferenceField('Games')
    player = ReferenceField('Players')
    gamemap = ReferenceField('Gamemaps')
    gametype = IntField()
    num_players = IntField()
    vote = IntField()


class Games(Document):
    timestamp = StringField()
    mapname = StringField()
    gamemap = ReferenceField('Gamemaps')
    gametype = IntField()
    players = ListField(ReferenceField('Players'))
    votes = ListField(ReferenceField('Votes'))
    state = StringField()
    start = StringField()
    stop = StringField()
    num_players = IntField()
    current = BooleanField()
    options = DictField()

    # fields allowed to be updated by context info
    update_fields = ['mapname', 'gametype', 'state', 'start', 'stop', 'num_players', 'current']


class PlayerVotes(Document):
    id = DictField(primary_key=True)
    value = FloatField()


class IntermediatePlaylist(Document):
    id = DictField(primary_key=True)
    value = DictField()


class PlaylistItems(Document):
    gamemap = ReferenceField('Gamemaps')
    votes = ListField(ReferenceField('Votes'))
    gametype = IntField(default=0)
    score = FloatField(default=0)
    modifiers = ListField(DictField())
