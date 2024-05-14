from random import shuffle
from players.models import Player, Team


def divide_players(players_list: list[Player]) -> tuple[list[Player], list[Player]]:
    """
    Divide a list of players into two lists.

    Args:
    -----
        players_list (list[Player]): List of players.

    Returns:
    --------
        tuple[list[Player], list[Player]]: Tuple with two lists of players.

    """
    shuffle(players_list)
    num_members = len(players_list)
    middle_index = num_members // 2
    return players_list[:middle_index], players_list[middle_index:]


def create_default_teams(
    team1_name: str, team2_name: str, players_list: list[Player]
) -> tuple[Team, Team]:
    """
    Create two teams with the given players.

    Args:
    -----
        team1_name (str): Name of the first team.
        team2_name (str): Name of the second team.
        team1_players_list (list[Player]): List of players for the first team.
        team2_players_list (list[Player]): List of players for the second team.

    Returns:
    --------
        tuple[Team, Team]: Tuple with two teams.

    """
    team1 = Team.objects.get_or_create(name=team1_name)[0]
    team2 = Team.objects.get_or_create(name=team2_name)[0]
    team1_players_list, team2_players_list = divide_players(players_list)

    team1.players.set(team1_players_list)
    team1.leader = team1_players_list[0]
    team1.save()

    team2.players.set(team2_players_list)
    team2.leader = team2_players_list[0]
    team2.save()
    return team1, team2
