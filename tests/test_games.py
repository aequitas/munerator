from munerator.games import Game


def test_game_mapstring():
    expected_mapstring = ("set g_warmup 0;set g_doWarmup 0;set g_spawnprotect 2000;set g_speed 320;"
                          "set g_gravity 800;set g_knockback 1000;set map_restart 0;set g_instantgib 0;"
                          "set g_vampire 0;set g_regen 0;set g_rockets 0;set g_catchup 0;set g_respawntime 0;"
                          "g_catchup 5;set g_motd no special mode;set fraglimit 16;set g_gametype 0;"
                          "map mapname")

    game = Game('mapname', 0, 4)

    assert game.mapstring() == expected_mapstring


def test_game_mapstring_special():
    expected_mapstring = ("set g_warmup 0;set g_doWarmup 0;set g_spawnprotect 2000;set g_speed 320;"
                          "set g_gravity 800;set g_knockback 1000;set map_restart 0;set g_instantgib 0;"
                          "set g_vampire 0;set g_regen 0;set g_rockets 0;set g_catchup 0;set g_respawntime 0;"
                          "g_catchup 5;set g_instantgib 2;set g_motd instagib;set fraglimit 16;"
                          "set g_gametype 0;map mapname")

    game = Game('mapname', 0, 4, 'instagib')

    assert game.mapstring() == expected_mapstring


def test_game_mapstring_team():
    expected_mapstring = ("set g_warmup 0;set g_doWarmup 0;set g_spawnprotect 2000;set g_speed 320;"
                          "set g_gravity 800;set g_knockback 1000;set map_restart 0;set g_instantgib 0;"
                          "set g_vampire 0;set g_regen 0;set g_rockets 0;set g_catchup 0;set g_respawntime 0;"
                          "set g_teamAutoJoin 0;set g_teamForceBalance 1;set capturelimit 5;set g_respawntime 5;"
                          "set g_motd no special mode;set fraglimit 16;set g_gametype 4;map mapname")

    game = Game('mapname', 4, 4)

    assert game.mapstring() == expected_mapstring


def test_replace_nextmap():
    expected_mapstring = ("set nextmap \"set g_warmup 0;set g_doWarmup 0;set g_spawnprotect 2000;set g_speed 320;"
                          "set g_gravity 800;set g_knockback 1000;set map_restart 0;set g_instantgib 0;"
                          "set g_vampire 0;set g_regen 0;set g_rockets 0;set g_catchup 0;set g_respawntime 0;"
                          "set g_teamAutoJoin 0;set g_teamForceBalance 1;set capturelimit 5;set g_respawntime 5;"
                          "set g_motd no special mode;set fraglimit 16;set g_gametype 4;map mapname;"
                          "set nextmap vstr map01\";")

    game = Game('mapname', 4, 4)

    assert game.nextmapstring('vstr map01') == expected_mapstring
