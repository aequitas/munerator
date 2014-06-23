from munerator.trans import translate, regexes
import pytest


@pytest.mark.parametrize("line,kind", [
    [r'126031: client:4 health:-19 damage:20 armor:0', 'hit'],
    [r'442831: client:0 health:40 damage:6 armor:0', 'hit'],
    [r'Kill: 1 6 1: Ukrainian General killed yakherder by MOD_SHOTGUN', 'kill'],
    [r'0:48 Item: 0 item_quad', 'quad'],
    [r'say: -[aequitas]-: instagib', 'say'],
    [r'-[aequitas]-^7: instagib', None],
    [r'Kill: 1022 5 20: <world> killed Gunnaway by MOD_SUICIDE', 'kill'],
    [r'Kill: 1022 0 16: <world> killed -[aequitas]- by MOD_LAVA', 'kill'],
    [r'Kill: 1022 0 16: <world> killed Some nick by MOD_LAVA', 'kill'],
    [r'Kill: 1022 0 16: <world> killed ^1color by MOD_LAVA', 'kill'],
    [r'0:37 ClientUserinfoChanged: 0 n\-[aequitas]-\t\0\model\assassin/ghost\hmodel\assassin/ghost\g_redteam\\'
        r'g_blueteam\\c1\3\c2\3\hc\100\w\0\l\0\tt\0\tl\0\id\9982DEAC44F27E0622FCF0FC6C540F45', 'clientuserinfochanged'],
    [r'0:10 ClientUserinfoChanged: 1 n\Broadklin\t\0\model\gargoyle/stone\hmodel\gargoyle/stone\c1\4\c2\5\hc\100'
        r'\w\0\l\0\skill\ 4.00\tt\0\tl\0\id\\', 'clientuserinfochanged'],
])
def test_translations(line, kind):
    result = list(translate(line, regexes))
    if kind:
        assert result[0][0] == kind
    else:
        assert not result


@pytest.mark.parametrize("line,key,value", [
    [r'0:01 ClientUserinfoChanged: 0 n\-[aequitas]-\t\2\model\assassin/ghost\hmodel\assassin/ghost\g_redteam\\g_blue'
        r'team\\c1\3\c2\3\hc\100\w\0\l\0\tt\0\tl\1\id\9982DEAC44F27E0622FCF0FC6C540F45', 'player_name', '-[aequitas]-'],
    [r'0:01 ClientUserinfoChanged: 0 n\-[aequitas]-\t\2\model\assassin/ghost\hmodel\assassin/ghost\g_redteam\\'
        r'g_blueteam\\c1\3\c2\3\hc\100\w\0\l\0\tt\0\tl\1\id\9982DEAC44F27E0622FCF0FC6C540F45', 'team_id', '2'],
    [r'0:01 ClientUserinfoChanged: 0 n\-[aequitas]-\t\1\model\assassin/ghost\hmodel\assassin/ghost\g_redteam\\'
        r'g_blueteam\\c1\3\c2\3\hc\100\w\0\l\0\tt\0\tl\1\id\9982DEAC44F27E0622FCF0FC6C540F45', 'team_id', '1'],
    [r'0:01 ClientUserinfoChanged: 0 n\-[aequitas]-\t\0\model\assassin/ghost\hmodel\assassin/ghost\g_redteam\\g_blue'
        r'team\\c1\3\c2\3\hc\100\w\0\l\0\tt\0\tl\1\id\9982DEAC44F27E0622FCF0FC6C540F45', 'team_id', '0'],
    [r'say: -[aequitas]-: instagib', 'text', 'instagib'],
    [r'0:10 ClientUserinfoChanged: 1 n\Broadklin\t\0\model\gargoyle/stone\hmodel\gargoyle/stone\c1\4\c2\5\hc\100'
        r'\w\0\l\0\skill\ 4.00\tt\0\tl\0\id\\', 'skill', '4.00'],
    [r'0:10 ClientUserinfoChanged: 1 n\Broadklin\t\0\model\gargoyle/stone\hmodel\gargoyle/stone\c1\4\c2\5\hc\100'
        r'\w\0\l\0\skill\ 4.00\tt\0\tl\0\id\\', 'guid', '1'],
    [r'Kill: 1022 5 20: <world> killed Gunnaway by MOD_SUICIDE', 'killer', '<world>'],
    [r'Kill: 1022 0 16: <world> killed -[aequitas]- by MOD_LAVA', 'killed', '-[aequitas]-'],
    [r'Kill: 1022 0 16: <world> killed Some nick by MOD_LAVA', 'killed', 'Some nick'],
    [r'Kill: 1022 0 16: <world> killed ^1color by MOD_LAVA', 'killed', '^1color']
])
def test_data(line, key, value):
    result = list(translate(line, regexes))
    assert result
    expect = result[0][1][key]
    assert expect == value
