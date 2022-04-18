from tournaments.factories import TournamentTeamFactory, TournamentTeamMemberFactory
from users.factories import UserFactory

users_list = []
users_captains = []
teams = []
for _ in range(1000):
    try:
        users_list.append(UserFactory.create())
    except:
        continue

for _ in range(100):
    captain = users_list[_]
    teams.append(TournamentTeamFactory.create(captain=captain))

team_size = teams[0].tournament.team_size
users_chunks = [users_list[x:x+team_size] for x in range(0, len(users_list), team_size)]

for i, team_chunk in enumerate(users_chunks):
    for user in team_chunk:
        TournamentTeamMemberFactory.create(user=user, team=teams[i-1])
