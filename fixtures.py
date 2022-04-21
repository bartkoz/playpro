from tournaments.factories import TournamentTeamFactory, TournamentTeamMemberFactory
from users.factories import UserFactory

users_list = []
users_captains = []
teams = []
for _ in range(500):
    try:
        users_list.append(UserFactory.create())
    except Exception as e:
        print(e)

for _ in range(100):
    captain = users_list[_]
    users_captains.append(captain)
    teams.append(TournamentTeamFactory.create(captain=captain))

users_list = [x for x in users_list if x not in users_captains]
team_size = teams[0].tournament.team_size - 1
users_chunks = [
    users_list[x : x + team_size] for x in range(0, len(users_list), team_size)
]

for i, team_chunk in enumerate(users_chunks):
    for user in team_chunk:
        TournamentTeamMemberFactory.create(user=user, team=teams[i - 1])
