class Game(object):
    specials = {
        "instagib": "set g_instantgib 2"
    }

    defaults = [
        "set g_warmup 0",
        "set g_doWarmup 0",
        "set g_spawnprotect 2000",
        "set g_speed 320",
        "set g_gravity 800",
        "set g_knockback 1000",
        "set map_restart 0",
        "set g_instantgib 0",
        "set g_vampire 0",
        "set g_regen 0",
        "set g_rockets 0",
        "set g_catchup 0"
    ]

    team_commands = [
        "set g_teamAutoJoin 0",
        "set g_teamForceBalance 1"
    ]

    catchup = "g_catchup 5"

    def __init__(self, mapname, gametype, num_players=3, special=None):
        self.mapname = mapname
        self.gametype = gametype
        self.num_players = num_players
        self.special = special

    @staticmethod
    def get_fraglimit(num_players):
        # increate fraglimit by 8 for every two players joining
        fraglimit = int(num_players) / 2 * 8
        fraglimit = fraglimit = max(10, min(fraglimit, 30))

        return fraglimit

    def mapstring(self, nextmap=None):
        cmds = list(self.defaults)

        # set gametype specific options
        if self.gametype in [3, 4, 5, 6, 7, 8, 9]:
            cmds += self.team_commands
        else:
            cmds.append(self.catchup)

        if self.special:
            cmds.append(self.specials[self.special])

        if self.special:
            cmds.append("set g_motd %s" % self.special)
        else:
            cmds.append("set g_motd ''")

        cmds.append("set fraglimit %s" % self.get_fraglimit(self.num_players))
        cmds.append("set g_gametype %s" % self.gametype)

        if nextmap:
            cmds.append('set nextmap "%s"' % nextmap)

        cmds.append("map %s" % self.mapname)

        return ";".join(cmds)

    def nextmapstring(self, nextmap=None):
        return 'set nextmap "%s";' % self.mapstring(nextmap).replace('"', '\\"')
