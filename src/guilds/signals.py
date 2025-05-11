

from django.dispatch import receiver
from django.db.models.signals import post_save
from guilds.models import Guild
from matches.models import Match, MatchConfig, Cvar, MatchConfigCvar
from matches.pydantic_schemas import SideChoice

def get_custom_cvars():
    """
    Helper function to get custom cvars.
    """
    cvars = [
        {
            'cvar': Cvar.objects.get(name="sv_cheats"),
            'value': True,
        },
        {
            'cvar': Cvar.objects.get(name="mp_startmoney"),
            'value': 16000,
        },
    ]
    return cvars

def get_cvars_for_match_config(match_config):
    """
    Helper function to get cvars for a given match config.
    """
    cvars = [
        {
            'cvar': Cvar.objects.get(name="matchzy_remote_log_url"),
            'value': "https://example.com/bo1_competitive",
        },
        {
            'cvar': Cvar.objects.get(name="matchzy_remote_log_header_key"),
            'value': "Authorization",
        },
        {
            'cvar': Cvar.objects.get(name="matchzy_remote_log_header_value"),
            'value': "Bearer YOUR_TOKEN",
        },
    ]
    return cvars

def create_match_config_cvars(match_config, custom_cvars=False):

    """
    Helper function to create MatchConfigCvar instances for a given match config.
    """
    cvars = get_cvars_for_match_config(match_config)
    for cvar in cvars:
        MatchConfigCvar.objects.create(
            match_config=match_config,
            cvar=cvar['cvar'],
            value=cvar['value'],
        )
    if custom_cvars:
        custom_cvars = get_custom_cvars()
        for cvar in custom_cvars:
            MatchConfigCvar.objects.create(
                match_config=match_config,
                cvar=cvar['cvar'],
                value=cvar['value'],
            )

def create_match_config(guild):
    """
    Helper function to create a match config.
    """
    map_sides_based_on_type = {
        Match.Type.BO1: [SideChoice.KNIFE],
        Match.Type.BO3: [SideChoice.KNIFE, SideChoice.TEAM1_CT, SideChoice.TEAM2_T],
        Match.Type.BO5: [SideChoice.KNIFE, SideChoice.TEAM1_CT, SideChoice.TEAM2_T],
    }

    configs_to_create = [
        {
            'name': "BO1 COMPETITIVE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO1,
            'shuffle_teams': False,
            'map_sides': map_sides_based_on_type[Match.Type.BO1],
            'players_per_team': 5,
        },
        {
            'name': "BO3 COMPETITIVE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO3,
            'shuffle_teams': False,
            'map_sides': map_sides_based_on_type[Match.Type.BO3],
            'players_per_team': 5,
        },
        {
            'name': "BO5 COMPETITIVE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO5,
            'shuffle_teams': False,
            'map_sides': map_sides_based_on_type[Match.Type.BO5],
            'players_per_team': 5,
        },
        {
            'name': "BO1 WINGMAN",
            'game_mode': MatchConfig.GameMode.WINGMAN,
            'type': Match.Type.BO1,
            'shuffle_teams': False,
            'map_sides': map_sides_based_on_type[Match.Type.BO1],
            'players_per_team': 2,
        },
        {
            'name': "BO3 WINGMAN",
            'game_mode': MatchConfig.GameMode.WINGMAN,
            'type': Match.Type.BO3,
            'shuffle_teams': False,
            'map_sides': map_sides_based_on_type[Match.Type.BO3],
            'players_per_team': 2,
        },
        {
            'name': "BO1 COMPETITIVE SHUFFLE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO1,
            'shuffle_teams': True,
            'map_sides': map_sides_based_on_type[Match.Type.BO1],
            'players_per_team': 5,
        },
        {
            'name': "BO3 COMPETITIVE SHUFFLE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO3,
            'shuffle_teams': True,
            'map_sides': map_sides_based_on_type[Match.Type.BO3],
            'players_per_team': 5,
        },
        {
            'name': "BO5 COMPETITIVE SHUFFLE",
            'game_mode': MatchConfig.GameMode.COMPETITIVE,
            'type': Match.Type.BO5,
            'shuffle_teams': True,
            'map_sides': map_sides_based_on_type[Match.Type.BO5],
            'players_per_team': 5,
        },
        {
            'name': "BO1 WINGMAN SHUFFLE",
            'game_mode': MatchConfig.GameMode.WINGMAN,
            'type': Match.Type.BO1,
            'shuffle_teams': True,
            'map_sides': map_sides_based_on_type[Match.Type.BO1],
            'players_per_team': 2,
        },
        {
            'name': "BO3 WINGMAN SHUFFLE",
            'game_mode': MatchConfig.GameMode.WINGMAN,
            'type': Match.Type.BO3,
            'shuffle_teams': True,
            'map_sides': map_sides_based_on_type[Match.Type.BO3],
            'players_per_team': 2,
        },
        {
            "name": "BO1 CUSTOM",
            "game_mode": MatchConfig.GameMode.COMPETITIVE,
            "type": Match.Type.BO1,
            "shuffle_teams": True,
            "map_sides": map_sides_based_on_type[Match.Type.BO1],
            "players_per_team": 5,
        }
    ]
    for config in configs_to_create:
        match_config_instance = MatchConfig.objects.create(
            name=config['name'],
            game_mode=config['game_mode'],
            type=config['type'],
            map_sides=config['map_sides'],
            players_per_team=config['players_per_team'],
            shuffle_teams=config['shuffle_teams'],
            clinch_series=False,
            guild=guild,
            map_pool=None,
        )
        create_match_config_cvars(match_config_instance, custom_cvars=True if "CUSTOM" in config['name'] else False)
        match_config_instance.save()

@receiver(post_save, sender=Guild)
def create_match_configs(sender, instance, created, **kwargs):
    """
    Signal to create a match config when a guild is created.
    """
    if created: 
        create_match_config(instance)