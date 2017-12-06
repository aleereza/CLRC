import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import datetime

# to use google sheets
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-CLRC.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

base_dir = os.getcwd()
client_sicret_dir = os.path.join(base_dir, 'client_sicret_dir')
CLIENT_SECRET_FILE = os.path.join(client_sicret_dir, 'client_secret.json')
APPLICATION_NAME = 'CLRC'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-CLRC.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def read_googlesheets(rangeName):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1e7kP27kCs-uPkf509RWpYC6rGZ-G3NKMBEUczXlGVKI'
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values')
    
    return values
#    if not values:
#        print('No data found.')
#    else:
#        print('Name, Major:')
#        for row in values:
#            # Print columns A and E, which correspond to indices 0 and 4.
#            print('%s, %s' % (row[0], row[4]))

class Search (object):
    #create search url
    
    #has problem, never changes paramiters
    parameters = {}
    city = 'vancouver'
    parameters['city'] = city
    query=''
    parameters['query'] = query
    search_distance= '10'
    parameters['search_distance'] = search_distance
    postal = 'V5A1S6'
    parameters['postal'] = postal
    min_price = '800'
    parameters['min_price'] = min_price
    max_price = '1500'
    parameters['max_price'] = max_price
    max_bedrooms = '1'
    parameters['max_bedrooms'] = max_bedrooms
    minSqft = '500'
    parameters['minSqft'] = minSqft
    availabilityMode = '0'
    parameters['availabilityMode'] = availabilityMode
    sort= 'date'
    parameters['sort'] = sort
    
    search_url = 'https://vancouver.craigslist.ca/search/apa?'
    
    
    def __init__ (self, **options):
        self.city = options.get('city')
        self.query = options.get('query')
        self.search_distance = options.get('search_distance')
        self.postal = options.get('postal')
        self.min_price = options.get('min_price')
        self.max_price = options.get('max_price')
        self.max_bedrooms = options.get('max_bedrooms')
        self.minSqft = options.get('minSqft')
        
                
    @property
    def url (self):
        for key, value in self.parameters.items():
            self.search_url = self.search_url + key + '=' + value + '&'
        return self.search_url
    
    
class Result (object):
# input : soup of search row: rows = s.find_all('li', class_ ='result-row' )
    def __init__ (self, row):
        self.link = row.find_all('a', class_ = 'result-title hdrlnk')[0]['href']
        temp_time = row.find_all('time', class_ = 'result-date')[0]['datetime']
        self.time = datetime.strptime(temp_time, "%Y-%m-%d %H:%M")
        self.price = row.find_all('span', class_ = 'result-price')[0].string
        self.id = row['data-pid']
        
#class ResultList (object):
#    
#    results_df = pd.DataFrame(columns = columns)

class Gsheet (object):
    def __init__ (self):
        rangeName = 'list!Z1:Z3'
        initials = read_googlesheets(rangeName)
        print(initials)
        self.frow = initials[0][0]
        self.lrow = initials[1][0]
        self.ltime = datetime.strptime(initials[2][0], "%Y-%m-%d %H:%M")
        
    
def find_new(url):
    #check the Result and compate to last date add if there was new rows build a data frame
    r = requests.get(url)
    c = r.content
    s = BeautifulSoup(c, 'html.parser')
    rows = s.find_all('li', class_ ='result-row' )
    sheet = Gsheet()
    last_time = sheet.ltime
    firs_row = sheet.frow
    last_row = sheet.lrow
    
    columns = ['id','link','price','time']    
    list_df = pd.DataFrame(columns = columns)
    
    df_row_index = 0
    for row in rows:
        sample = Result(row)
        #temp_time = sample.time
        if sample.time > last_time:
            df_row = [sample.__dict__[x] for x in columns]
            list_df.loc[df_row_index] = df_row
            df_row_index+=1
            #print(df_row)
    list_df.sort_values(by = ['time'],inplace = True, ascending = True)
    
    print(list_df)
        
 
    
if __name__ == '__main__':
#    try:
#        CITY = sys.argv[1]
#    except:
#        print "You need to include a city name and a query!\n"
#        sys.exit(1)
    search = Search()
    url = search.url
    print(url)
    
    
    
    find_new (url)
    
    #read_googlesheets()
    

    
    
    
    
        