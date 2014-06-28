import DS from "ember-data";

var Player = DS.Model.extend({
    name: DS.attr('string'),
    team: DS.attr('string'),
    online: DS.attr('boolean'),
    score: DS.attr('number'),
    names: DS.attr('raw'),
    skill: DS.attr('number'),    
    bot: DS.attr('boolean'),
    _updated: DS.attr('date')
});

Player.reopenClass({
    FIXTURES: [
        {
            id: '2394808AFSDFAFS',
            name: '-[aequitas]-',
            team: 'red',
            online: true,
            score: 42,
            names: ['old_nickname']
        },
        {
            id: '23948ASDF08AFSDFAFS',
            name: 'n^100^0b',
            team: 'red',
            online: true,
            score: 0
        },
        {
            id: '23948SFADFJKLASDF08AFSDFAFS',
            name: 'colors^11^22^33^44^55^66^77^0w00t',
            team: '',
            online: false,
            score: 0
        }
    ]
});

export default Player;
