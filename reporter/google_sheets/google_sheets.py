import os
from random import randrange

import httplib2
from environs import Env
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

sheet__id = "1FQ5Gg1SbqZpRgOI6quj0gYyk0IW4JUjd4BbrPlZ5N1A"


class GoogleSheetWorker:

    def __init__(self):
        self._sheet_id = None
        self.sheet = self.get_service_sacc().spreadsheets()
        self._developer_key = None

    @property
    def sheet_id(self):
        if self._sheet_id is None:
            self._sheet_id = self._get_sheet_id()
            return self._sheet_id
        return self._sheet_id

    def _get_sheet_id(self) -> str:
        env: Env = Env()
        env.read_env('.env')
        return env('GOOGLE_SHEET_ID')

    @property
    def developer_key(self):
        if self._developer_key is None:
            self._developer_key = self._get_developer_key()
            return self._developer_key
        return self._developer_key

    def _get_developer_key(self) -> str:
        env: Env = Env()
        env.read_env('.env')
        return env('GOOGLE_DEVELOPER_KEY')

    def get_service_simple(self):
        print()
        return build('sheets', 'v4', developerKey=self.developer_key)

    def get_service_sacc(self):
        creds_json = os.path.dirname(__file__) + "/credentials/AIPOcred.json"
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
        return build('sheets', 'v4', http=creds_service)

    # https://docs.google.com/spreadsheets/d/xxx/edit#gid=0

    # https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/sheets_v4.spreadsheets.html

    @staticmethod
    def get_values():
        values = [[randrange(10, 99)]]
        values = [[randrange(10, 99) for _ in range(0, 6)]]
        print()
        # values = [[randrange(10, 99)] for _ in range(0, 3)]
        # values = [[randrange(10, 99) for _ in range(0, 3)] for _ in range(0, 3)]
        print()
        return values

    def update_data_in_row(self, value):
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update
        resp = self.sheet.values().update(
            spreadsheetId=self.sheet_id,
            range="Лист1!A1",
            valueInputOption="RAW",
            body={'values': value}).execute()
        print(resp)

    def append_data_in_row(self, *value, sheet="Лист1!"):
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
        print()
        resp = self.sheet.values().append(
            spreadsheetId=self.sheet_id,
            range=f"{sheet}A1",
            valueInputOption="RAW",
            # insertDataOption="INSERT_ROWS",
            body={'values': [[*value]]}).execute()
        print(resp)

    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate
    # body = {
    #     'valueInputOption' : 'RAW',
    #     'data' : [
    #         {'range' : 'Лист2!D2', 'values' : get_values()},
    #         {'range' : 'Лист2!H4', 'values' : get_values()}
    #     ]
    # }

    # resp = sheet.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()


if __name__ == '__main__':
    a = GoogleSheetWorker()
    a.append_data_in_row("sdasdas", 'dasdsadsa', 123123)
