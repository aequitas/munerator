from mongoengine import Document, ListField, StringField, IntField, BooleanField, ReferenceField


class Players(Document):
    guid = StringField()
    name = StringField()
    names = ListField(StringField())
    online = BooleanField()
    score = IntField()
    team = StringField()
    team_id = IntField()


class Games(Document):
    game_id = StringField()
    mapname = StringField()
    players = ListField(ReferenceField(Players))
    state = StringField()
    start = StringField()
    stop = StringField()
    num_players = IntField()
    current = BooleanField()
