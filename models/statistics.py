from google_sheets_services.google_sheets_service import get_by_index

class Statistics:
    
    date = None
    username = None
    location = None
    approaches = None
    shorts = None
    closings = None
    forms = None
    trust_pays = None
    supporters = None
    comments = None

    def __init__(self, statistics_list: list = None, row_id: int = None) -> None:
        row_id = row_id
        self.date = get_by_index(statistics_list,0)
        self.username = get_by_index(statistics_list,1)
        self.location = get_by_index(statistics_list,2)
        self.approaches = get_by_index(statistics_list,3)
        self.shorts = get_by_index(statistics_list,4)
        self.closings = get_by_index(statistics_list,5)
        self.forms = get_by_index(statistics_list,6)
        self.trust_pays = get_by_index(statistics_list,7)
        self.supporters = get_by_index(statistics_list,8)
        self.comments = get_by_index(statistics_list,9)

    def get_statistics_list(self) -> list:
        return [self.date, self.username, self.location, self.approaches, 
        self.shorts, self.closings, self.forms, self.trust_pays, self.supporters, self.comments]

