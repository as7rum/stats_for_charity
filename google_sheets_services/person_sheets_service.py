from google_sheets_services.google_sheets_service import GoogleSheetsService
from models.person import Person
import pprint

from config.config import GOOGLE_SHEETS_DOC_ID, CREDENTIALS_FILE

class PersonSheetsService(GoogleSheetsService):

    def __init__(self, creds_file: str = CREDENTIALS_FILE, spreadsheet_id: str = GOOGLE_SHEETS_DOC_ID) -> None:
        super().__init__(creds_file, spreadsheet_id)

    def get_persons(self) -> list[Person]:
        values = self.get_values('persons')[1:]
        return list(map(lambda x: Person(x[1],x[0]), enumerate(values)))
    
    def get_person(self, user_id: str) -> Person:
        id = str(user_id)
        values = self.get_persons()
        person = next(filter(lambda x: x.id == id, values), None)
        if person:
            #person = Person(person_data)
            return person

    def get_person_by_username(self, username: str) -> Person:
        username = str(username)
        values = self.get_persons()
        person = next(filter(lambda x: x.username == username, values), None)
        if person:
            return person

    def get_person_row(self, user_id: str):
        id = str(user_id)
        values = self.get_values('persons')
        person_data = next(filter(lambda x: x[1][0] == id, enumerate(values)), None)
        return person_data[0]
    
    def add_person(self, person: Person):
        super().add_data('persons', person.get_values_list())

    def person_data_update(self, person: Person):
        super().update_data('persons', person.row_id, person.get_values_list())
