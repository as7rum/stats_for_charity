from google_sheets_services.google_sheets_service import GoogleSheetsService
from models.statistics import Statistics

from config.config import GOOGLE_SHEETS_DOC_ID, CREDENTIALS_FILE

class PersonSheetsService(GoogleSheetsService):
    
    def __init__(self, creds_file: str = CREDENTIALS_FILE, spreadsheet_id: str = GOOGLE_SHEETS_DOC_ID) -> None:
        super().__init__(creds_file, spreadsheet_id)

    def get_statistics(self) -> list[Statistics]:
        values = self.get_values('statistics')[1:]
        return list(map(lambda x: Statistics(x[1],x[0]), enumerate(values)))

    def get_statistics_by_person_username(self, username: str) -> Statistics:
        stats = self.get_statistics
        person_stats = next(filter(lambda x: x.username == username, stats), None)
        if person_stats:
            return person_stats

    def get_statistics_by_date(self, date: str) -> Statistics:
        stats = self.get_statistics
        date_stats = next(filter(lambda x: x.date == date, stats), None)
        if date_stats:
            return date_stats

    def get_statistics_by_location(self, location: str) -> Statistics:
        stats = self.get_statistics
        location_stats = next(filter(lambda x: x.location == location, stats), None)
        if location_stats:
            return location_stats

    def add_person(self, stats: Statistics):
        super().add_data('statistics', stats.get_statistics_list())

    def person_data_update(self, stats: Statistics):
        super().update_data('statistics', stats.row_id, stats.get_statistics_list())