from functions import *
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

#retrieves credentials from Google Service Account to log in
credentials = ServiceAccountCredentials.from_json_keyfile_name('data.json', scope)
gc = gspread.authorize(credentials)

#import population codes spreadsheet to pandas
pops = gc.open_by_key('1nP3mdssbSH9fftb8FHq9J8tFXHI0dqcARhRJ3mMpgGY')
p_sheet = pops.sheet1
pop = pd.DataFrame(p_sheet.get_all_records())

#import cordinate spreadsheet to pandas
cords = gc.open_by_key('1c5ZbJPPIoIOdYjGtkXLjfFyUlZcN0DSgaSnkYevEdFw')
c_sheet = cords.sheet1
cord = pd.DataFrame(c_sheet.get_all_records())

#import allele spreadsheet to pandas
alleles = gc.open_by_key('1SzXv3RQIim-eYhW4-OtVjveDd9Ph6QuXSTDTXqcN0ug')
a_sheet = alleles.sheet1
al = pd.DataFrame(a_sheet.get_all_records())

#import trait info spreadsheet to pandas
traits = gc.open_by_key('1yZCN3vkQWZLQea1xOvfAb4OzfM8zqN4tQn44obWT7m4')
t_sheet = traits.sheet1
trait = pd.DataFrame(t_sheet.get_all_records())

#merging data onto one database
flt = pd.merge(cord, al, copy=False, on='CODE')

res = pd.merge(flt, trait, copy=False, on='RS')

full = pd.merge(res, pop, copy=False, on='CODE')

#converts cordinate and allele data to numpy array
array = flt.as_matrix()
