import requests
from bs4 import BeautifulSoup
import pandas as pd
import pytz

# Get Park IDs **************************************************************

url = "https://queue-times.com/parks.json"
response = requests.get(url)

if response.status_code == 200:
    parks_data = response.json()

# put the names of the parks you want to know the ID of here
parks = {
    'Animal Kingdom',
    'Disney California Adventure',
    'Disney Hollywood Studios',
    'Disney Magic Kingdom',
    'Disneyland',
    'Epcot',
    'Islands Of Adventure At Universal Orlando',
    'Universal Studios At Universal Orlando',
    'Legoland California',
    'Cedar Point',
    'Dorney Park',
    'Six Flags Discovery Kingdom',
    'Six Flags Great Adventure',
    'Six Flags St. Louis'
}

# this code will print out the park IDs

#for group in parks_data:
#    all_parks = group.get('parks', [])

#    for park in all_parks:
#        park_id = park.get('id', '')
#        park_name = park.get('name', '')

#        if park_name in parks:
#            print(f"Park ID: {park_id}")
#            print(f"Park Name: {park_name}")
#            print()

# Function to collect API data **********************************************

def get_park_data(ID):
    url = f"https://queue-times.com/parks/{ID}/queue_times.json"
    response = requests.get(url)

    if response.status_code == 200:
        park_data = response.json()
    else:
        print(f"Failed to fetch data for park {ID}")
        return None

    lands_data = park_data.get('lands', [])

    # create empty lists
    lands = []
    attractions = []
    is_open_list = []
    wait_times = []
    last_updated_list = []

    # iterate over each land
    for land in lands_data:
        land_name = land.get('name')

        # make sure the parks have a 'rides' id
        rides = land.get('rides', [])

        # iterate over the rides in each land
        for ride in rides:
            ride_name = ride.get('name')
            is_open = ride.get('is_open')
            wait_time = ride.get('wait_time')
            last_updated = ride.get('last_updated')

            # append data to lists
            lands.append(land_name)
            attractions.append(ride_name)
            is_open_list.append(is_open)
            wait_times.append(wait_time)
            last_updated_list.append(last_updated)

    # create df from the lists
    park_df = pd.DataFrame({
        'land': lands,
        'attraction': attractions,
        'is_open': is_open_list,
        'wait_time': wait_times,
        'last_updated': last_updated_list
    })

    return park_df

# Assemble df for my selected parks *******************************************

parks_info = [
    (8, 'Animal Kingdom'),
    (17, 'California Adventure'),
    (7, 'Hollywood Studios'),
    (6, 'Magic Kingdom'),
    (16, 'Disneyland'),
    (5, 'EPCOT'),
    (64, 'Islands of Adventure'),
    (65, 'Universal Studios Orlando'),
    (33, 'Six Flags Discovery Kingdom'),
    (36, 'Six Flags St. Louis'),
    (37, 'Six Flags Great Adventure'),
    (279, 'Legoland California'),
    (50, 'Cedar Point'),
    (69, 'Dorney Park')
]

all_parks = []

for park_id, park_name in parks_info:
    park_data = get_park_data(park_id)
    park_data['park'] = park_name
    all_parks.append(park_data)

all_parks = pd.concat(all_parks, ignore_index=True)

# update timezone to MST
all_parks['last_updated'] = pd.to_datetime(all_parks['last_updated'], format="%Y-%m-%d %H:%M:%S%z")
mst_timezone = pytz.timezone("US/Mountain")
all_parks['last_updated'] = all_parks['last_updated'].apply(lambda x: x.astimezone(mst_timezone))

col_order = [1,2,3,4,5,0]
all_parks = all_parks.iloc[:, col_order]

print(all_parks)

# Assemble df for my selected parks *******************************************

# read in data from each API call
# add columns for the day and time of day
fri_morning = pd.read_csv("friday_morning.csv")
fri_morning['day'] = 'Friday'
fri_morning['time'] = 'Morning'

fri_afternoon = pd.read_csv("friday_afternoon.csv")
fri_afternoon['day'] = 'Friday'
fri_afternoon['time'] = 'Afternoon'

fri_evening = pd.read_csv("fri_evening.csv")
fri_evening['day'] = 'Friday'
fri_evening['time'] = 'Evening'

sat_morning = pd.read_csv("sat_morning.csv")
sat_morning['day'] = 'Saturday'
sat_morning['time'] = 'Morning'

sat_afternoon = pd.read_csv("sat_afternoon.csv")
sat_afternoon['day'] = 'Saturday'
sat_afternoon['time'] = 'Afternoon'

sat_evening = pd.read_csv("sat_evening.csv")
sat_evening['day'] = 'Saturday'
sat_evening['time'] = 'Evening'

# combine Friday and Saturday dataframes
friday_combined = pd.concat([fri_morning, fri_afternoon, fri_evening], ignore_index=True)
saturday_combined = pd.concat([sat_morning, sat_afternoon, sat_evening], ignore_index=True)

# combine the combined DataFrames
combined = pd.concat([friday_combined, saturday_combined], ignore_index=True)

# pivot for wait_time
wait_time_pivoted = combined.pivot_table(index=['park', 'land', 'attraction', 'day'],
                                        columns=['time'], values='wait_time', aggfunc='first')

# pivot for is_open
is_open_pivoted = combined.pivot_table(index=['park', 'land', 'attraction', 'day'],
                                       columns=['time'], values='is_open', aggfunc='first')

# rename colums using either W or I and the first two letters
wait_time_pivoted.columns = [f'W{col[0]}{col[1]}' for col in wait_time_pivoted.columns]
is_open_pivoted.columns = [f'I{col[0]}{col[1]}' for col in is_open_pivoted.columns]

# combine the pivoted dataframes
pivoted = pd.concat([wait_time_pivoted, is_open_pivoted], axis=1)

# reset index, which makes day a column
pivoted.reset_index(inplace=True)

# reorder columns
reordered_columns = ['attraction', 'land', 'park', 'day', 'IMo', 'IAf', 'IEv', 'WMo', 'WAf', 'WEv']
pivoted = pivoted[reordered_columns]

pivoted = pivoted.rename(columns={
    'IMo': 'is_open_M',
    'IAf': 'is_open_A',
    'IEv': 'is_open_E',
    'WMo': 'wait_time_M',
    'WAf': 'wait_time_A',
    'WEv': 'wait_time_E'
})

# Display the pivoted and reordered DataFrame
print(pivoted)


pivoted.to_csv("wait_times.csv")





