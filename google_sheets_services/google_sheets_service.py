import pprint

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from config.config import SCOPES, GOOGLE_SHEETS_DOC_ID, CREDENTIALS_FILE

class GoogleSheetsService:
    GOOGLE_SHEETS_DOC_ID = GOOGLE_SHEETS_DOC_ID
    SCOPES = SCOPES
    CREDENTIALS_FILE = CREDENTIALS_FILE

    service = None

    def __init__(self, creds_file: str = CREDENTIALS_FILE, 
    spreadsheet_id: str = GOOGLE_SHEETS_DOC_ID) -> None:
        self.creds_file = creds_file
        self.spreadsheet_id = spreadsheet_id

    def get_values(self, range: str) -> dict:
        service = self.__create_service()
        values = self.__get_values_from_server(service)
        result = values.get(
                spreadsheetId=self.spreadsheet_id,
                range = range,
                majorDimension='ROWS'
                ).execute()
        return result['values']

    def add_data(self, range: str, values: list):
        service = self.__create_service()
        values_for_adding = service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range = range,
            valueInputOption = 'USER_ENTERED',
            body = {'majorDimension': 'ROWS',
                    'values': [values]}
        ).execute()

    def update_data(self,chosen_list: str, row_id: int, values: list):
        service = self.__create_service()
        row_id += 2
        range = f'{chosen_list}!A{row_id}:Z{row_id}'
        values_for_adding = service.spreadsheets().values().batchUpdate(
        spreadsheetId=self.spreadsheet_id,
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data':{
                'range': range,
                'majorDimension': 'ROWS',
                'values': [values]}}    
        ).execute()
    
    def __create_service(self) -> None:
        """
        Getting service for sheets
        """
        creds_service = ServiceAccountCredentials.from_json_keyfile_name(
                self.creds_file,
                self.SCOPES
                ).authorize(httplib2.Http())
        return build('sheets', 'v4', http=creds_service)#, cache_discovery=False)

    def __get_values_from_server(self, service):
        return service.spreadsheets().values()
    

def get_by_index(array, index):
    if array != None and 0 <= index < len(array):
        return array[index]
    return None
# doc_first = GoogleSheetsService()
# doc_first.write_values('persons!A1:J1', [['Айнар', 'SOS', 'Сити Молл', '14.12.2022', 
# '242', '18', '5', '3', '2', '1']])
#pprint.pprint(doc_first.get_values(RANGE_NAME))
