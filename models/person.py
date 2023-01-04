from google_sheets_services.google_sheets_service import get_by_index

class Person:

    id = None
    username = None
    name = None
    birthdate = None
    chief = None
    job_title = None
    description = None
    team = None

    def __init__(self, person_data: list = None, row_id: int = None) -> None:        
        self.row_id = row_id
        self.id = get_by_index(person_data,0)
        self.username = get_by_index(person_data,1)
        self.name = get_by_index(person_data,2)
        self.birthdate = get_by_index(person_data,3)
        self.chief = get_by_index(person_data,4)
        self.job_title = get_by_index(person_data,5)
        self.description = get_by_index(person_data,6)
        self.team = get_by_index(person_data,7)

    def get_values_list(self) -> list:
        return [self.id, self.username, self.name, self.birthdate, 
        self.chief, self.job_title, self.description, self.team]