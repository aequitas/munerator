__all__ = ['Players', 'Games', 'Votes']

from mongoengine import (BooleanField, Document, IntField, DictField,
                         ListField, ReferenceField, StringField)


class Players(Document):
    guid = StringField()
    name = StringField()
    names = ListField(StringField())
    online = BooleanField()
    score = IntField()
    team = StringField()
    team_id = IntField()


class Games(Document):
    timestamp = StringField()
    mapname = StringField()
    gametype = IntField()
    players = ListField(ReferenceField(Players))
    state = StringField()
    start = StringField()
    stop = StringField()
    num_players = IntField()
    current = BooleanField()
    options = DictField()


class Votes(Document):
    game = ReferenceField(Games)
    player = ReferenceField(Players)
    vote = IntField()
