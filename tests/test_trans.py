from munerator.trans import translate, regexes, handle_line
import pytest
from mock import Mock


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
    [r"cmd:getstatus response_type:statusResponse response:\\\\g_obeliskRespawnDelay\\\\10\\\\bot_minplayers"
        r"\\\\0\\\\sv_allowDownload\\\\1"
        r"\\\\sv_privateClients\\\\0\\\\dmflags\\\\72\\\\fraglimit\\\\10\\\\timelimit\\\\100\\\\sv_hostname\\\\Brensen"
        r" OpenArena Server\\\\sv_maxclients\\\\32\\\\sv_minRate\\\\0\\\\sv_maxRate\\\\25000\\\\sv_minPing\\\\0\\\\sv_"
        r"maxPing\\\\400\\\\sv_floodProtect\\\\1\\\\sv_dlURL\\\\http://quake.brensen.com\\\\g_maxGameClients\\\\32"
        r"\\\\videoflags\\\\7\\\\capturelimit\\\\5\\\\g_doWarmup\\\\0\\\\g_allowVote\\\\1\\\\g_voteGametypes\\\\/0/3/"
        r"4/\\\\g_voteMaxTimelimit\\\\40\\\\g_voteMinTimelimit\\\\10\\\\g_voteMaxFraglimit\\\\100\\\\g_voteMinFrag"
        r"limit\\\\10\\\\g_delagHitscan\\\\1\\\\elimination_roundtime\\\\120\\\\g_lms_mode\\\\0\\\\version\\\\io"
        r"q3+oa 1.36_SVN1910M linux-x86_64 Dec 25 2011\\\\protocol\\\\71\\\\g_gametype\\\\0\\\\mapname\\\\alkdm13\\\\g"
        r"amename\\\\baseoa\\\\elimflags\\\\0\\\\voteflags\\\\215\\\\g_needpass\\\\0\\\\g_enableDust\\\\0\\\\g_enable"
        r"Breath\\\\0\\\\g_rockets\\\\0\\\\g_instantgib\\\\0\\\\g_altExcellent\\\\0\\\\g_timestamp\\\\2014-06-28 "
        r"13:38:20", 'getstatus'],
    [r"cmd:getstatus response_type:statusResponse response:\\\\g_obeliskRespawnDelay\\\\10\\n')", 'getstatus'],
    [r"cmd:status response_type:print response:  0     0   57 test^7                0 82.161.93.152"
     r"         15309 25000", 'clientstatus']
])
def test_translations(line, kind):
    result = list(translate(line, regexes))
    if kind:
        assert result
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
    [r'Kill: 1022 0 16: <world> killed ^1color by MOD_LAVA', 'killed', '^1color'],
    [r"cmd:getstatus response_type:statusResponse response:\\\\g_obeliskRespawnDelay\\\\10",
        'g_obeliskRespawnDelay', '10'],
    [r"cmd:getstatus response_type:statusResponse response:\\\\g_obeliskRespawnDelay\\\\10\\\\bot_minplayers\\\\0"
        r"\\\\sv_allowDownload\\\\1\\\\sv_privateClients\\\\0\\\\dmflags\\\\72\\\\fraglimit\\\\10\\\\timelimit"
        r"\\\\100\\\\sv_hostname\\\\Brensen13:38:20", 'dmflags', '72'],
    [r"cmd:status response_type:print response:  0     0   57 test^7                0 82.161.93.152"
     r"         15309 25000')", 'score', '0'],
    [r"cmd:status response_type:print response:  0     0   53 test name^7           0 82.161.93.152"
     r"         31203 25000')", 'player_name', 'test name']
])
def test_data(line, key, value):
    result = list(translate(line, regexes))
    assert result
    expect = result[0][1][key]
    assert expect == value


def test_line_handling():
    mock_socket = Mock()
    handle_line('0', 'say: -[aequitas]-: instagib', mock_socket)

    data = {'text': 'instagib', 'kind': 'say', 'player_name': '-[aequitas]-', 'timestamp': '0'}

    mock_socket.send_json.assert_called_with(data)


def test_line_unhandling():
    mock_socket = Mock()
    handle_line('0', 'E_nosuchevent', mock_socket)

    data = {'raw': 'E_nosuchevent', 'kind': 'unhandled', 'timestamp': '0'}

    mock_socket.send_json.assert_called_with(data)
