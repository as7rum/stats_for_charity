from google_sheets_services.person_sheets_service import PersonSheetsService
from google_sheets_services.google_sheets_service import GoogleSheetsService
from models.person import Person

# service = GoogleSheetsService()

# values = service.get_values('persons')[1:]
# values_list = list(map(lambda x: Person(x[1],x[0]), enumerate(values)))
# id = '424546851'
# #Уже полученный объект Person
# person_data = next(filter(lambda x: x.id == id, values_list), None)
# #person = Person(person_data)# принимает person_data: list, row_id: int
# print(person_data.username)

service = PersonSheetsService()

values = service.get_persons()
username = 'as7rum'
person = next(filter(lambda x: x.username == username, values), None)
if person.team:
    team_list = person.team.split(',')[:-1]
    team_second_list = team_list
    team_second_list.append('me')
    team_str = ''.join(str(x + ',') for x in team_second_list)
    person.team = team_str
    service.person_data_update(person)
else:
    message = "supermen"
    person.team = list().append(message)


# person_row = service.get_person_row(person.id)
# service.person_data_update(person)

# Попробовать вызвать get_values_list и посмотреть обновления

# print(team_str.split(',')[:-1])
print(person.get_values_list())