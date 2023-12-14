# load libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", "is_categorical_dtype")

# load data
parks = pd.read_csv("/Users/justinross/Documents/BYU/stat386/ThemeParkWaitTimes_EDA/wait_times.csv")

# Countplot of number of attractions in each park ********************************************************
plt.style.use('ggplot')
plt.figure(figsize=(10, 5))

# remove duplicates (each park is listed twice for friday and saturday)
parks_no_duplicates = parks.drop_duplicates(subset='attraction')

# plot
sns.countplot(x='park', data=parks_no_duplicates)
plt.xticks(rotation=45) # improves readability
plt.title('Number of Attractions in Each Park')
plt.xlabel('Theme Park')
plt.xticks(ha='right')
plt.ylabel('Number of Attractions')
plt.show()


# Top 5 wait times for each time of day (morning, afternoon, evening) ************************************

def get_top_attractions_by_time(data, wait_times):
    top_attractions = data.groupby('park').apply(lambda x: x.loc[x[wait_times].idxmax()])
    top_attractions = top_attractions.sort_values(by=wait_times, ascending=False)
    top_attractions = top_attractions.head()
    top_attractions.reset_index(drop = True, inplace = True)
    top_attractions = top_attractions[['park', 'attraction', wait_times]]
    return top_attractions

# morning
top_morning_attractions = get_top_attractions_by_time(parks, 'wait_time_M')

# afternoon
top_afternoon_attractions = get_top_attractions_by_time(parks, 'wait_time_A')

# evening
top_evening_attractions = get_top_attractions_by_time(parks, 'wait_time_E')


# Number of Attractions vs Average Wait Time by Park *****************************************************

# exclude attractions with zero wait time
parks_filtered = parks[(parks['wait_time_M'] != 0) & (parks['wait_time_A'] != 0) & (parks['wait_time_E'] != 0)]

# for each park:
# count the number of attractions
# calculate average wait time for morning, afternoon, evening
park_stats = parks_filtered.groupby('park').agg(attraction_count=('attraction', 'count'),
                                                morning_avg = ('wait_time_M', 'mean'),
                                                afternoon_avg = ('wait_time_A', 'mean'),
                                                evening_avg = ('wait_time_E', 'mean'))

# calculate the total average wait time
park_stats['total_avg'] = park_stats[['morning_avg', 'afternoon_avg', 'evening_avg']].mean(axis=1)
park_stats.reset_index(inplace=True)

# plot
plt.figure(figsize=(10, 5))
sns.scatterplot(x='attraction_count', y='total_avg', data=park_stats, hue='park', s=100)
plt.xlabel('Number of Attractions')
plt.ylabel('Average Wait Time')
plt.title('Number of Attractions vs. Average Wait Time by Park')
plt.show()

# Ride Closures ******************************************************************************************

# this data is more useful for looking at individual or related parks
# this visualization will look at just the universal studios parks in Orlando
# we should also compare separate days

friday_df = parks[parks['day'] == 'Friday']
saturday_df = parks[parks['day'] == 'Saturday']
friday_df = friday_df[friday_df['park'].isin(['Islands of Adventure', 'Universal Studios Orlando'])]
saturday_df = saturday_df[saturday_df['park'].isin(['Islands of Adventure', 'Universal Studios Orlando'])]

# combine is_open columns for graphing
friday_melted_df = pd.melt(friday_df, value_vars=['is_open_M', 'is_open_A', 'is_open_E'], var_name='time_of_day', value_name='is_open')
saturday_melted_df = pd.melt(saturday_df, value_vars=['is_open_M', 'is_open_A', 'is_open_E'], var_name='time_of_day', value_name='is_open')

# combined plot
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Friday
axes[0].set_title('Closed Attractions: A Time-of-Day Comparison - Friday')
sns.countplot(x='time_of_day', hue='is_open', data=friday_melted_df, ax=axes[0])
axes[0].set_xlabel('Time of Day')
axes[0].set_ylabel('Number of Attractions')
axes[0].set_xticklabels(['Morning', 'Afternoon', 'Evening'])
axes[0].legend(title='Attraction Status', labels=['Closed', 'Open'], loc='upper right')

# Saturday
axes[1].set_title('Closed Attractions: A Time-of-Day Comparison - Saturday')
sns.countplot(x='time_of_day', hue='is_open', data=saturday_melted_df, ax=axes[1])
axes[1].set_xlabel('Time of Day')
axes[1].set_ylabel('Number of Attractions')
axes[1].set_xticklabels(['Morning', 'Afternoon', 'Evening'])
axes[1].legend(title='Attraction Status', labels=['Closed', 'Open'], loc='upper right')

plt.tight_layout()
plt.show()

# Wait Times Throughout the Day **************************************************************************

# separate Friday and Saturday for comparison
parks_filtered_friday = parks_filtered[parks_filtered['day'] == 'Friday']
parks_filtered_saturday = parks_filtered[parks_filtered['day'] == 'Saturday']

# combine wait times for graphing
melted_df_friday = pd.melt(parks_filtered_friday, value_vars=['wait_time_M', 'wait_time_A', 'wait_time_E'], var_name='time_of_day', value_name='wait_time')
melted_df_saturday = pd.melt(parks_filtered_saturday, value_vars=['wait_time_M', 'wait_time_A', 'wait_time_E'], var_name='time_of_day', value_name='wait_time')

# combined plot
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Friday
axes[0].set_title('Friday Wait Time Distribution')
sns.boxplot(x='time_of_day', y='wait_time', data=melted_df_friday, ax=axes[0])
axes[0].set_xlabel('Time of Day')
axes[0].set_ylabel('Wait Time (minutes)')
axes[0].set_xticklabels(['Morning', 'Afternoon', 'Evening'])

# Saturday
axes[1].set_title('Saturday Wait Time Distribution')
sns.boxplot(x='time_of_day', y='wait_time', data=melted_df_saturday, ax=axes[1])
axes[1].set_xlabel('Time of Day')
axes[1].set_ylabel('Wait Time (minutes)')
axes[1].set_xticklabels(['Morning', 'Afternoon', 'Evening'])

plt.tight_layout()
plt.show()

# violin plot

# combine wait times for graphing
melted_df = pd.melt(parks_filtered, id_vars=['day'], value_vars=['wait_time_M', 'wait_time_A', 'wait_time_E'], var_name='time_of_day', value_name='wait_time')

# x axis labels
day_order = ['Friday', 'Saturday']

# plot
ax = sns.violinplot(data=melted_df, x="time_of_day", y="wait_time", hue="day", split=True, cut=0, hue_order=day_order)
ax.set_xticklabels(['Morning', 'Afternoon', 'Evening'])
plt.title('Distribution of Wait Times')
plt.xlabel('Time of Day')
plt.show()

# Average Wait Times *************************************************************************************

# this data is more useful for looking at individual or related parks
# this visualization will look at just the Disney World parks

selected_parks = ['Animal Kingdom', 'Magic Kingdom', 'Hollywood Studios', 'EPCOT']
disney_world = parks_filtered[parks_filtered['park'].isin(selected_parks)]

# Filter for Friday
disney_world_fri = disney_world[disney_world['day'] == 'Friday']
melted_df_fri = pd.melt(disney_world_fri, id_vars=['day', 'attraction', 'park'], value_vars=['wait_time_M', 'wait_time_A'], var_name='time_of_day', value_name='wait_time')
melted_df_fri2 = pd.melt(disney_world_fri, id_vars=['day', 'attraction', 'park'], value_vars=['wait_time_A', 'wait_time_E'], var_name='time_of_day', value_name='wait_time')

# combined plots
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Friday
sns.pointplot(data=melted_df_fri, x='time_of_day', y='wait_time', hue='park', dodge=True, ax=axes[0])
axes[0].set_title('Friday Average Wait Times')
axes[0].set_xlabel('Time of Day')
axes[0].set_ylabel('Wait Time')
axes[0].set_xticklabels(['Morning', 'Afternoon'])

# Friday 2
sns.pointplot(data=melted_df_fri2, x='time_of_day', y='wait_time', hue='park', dodge=True, ax=axes[1])
axes[1].set_title('Friday Average Wait Times')
axes[1].set_xlabel('Time of Day')
axes[1].set_ylabel('Wait Time')
axes[1].set_xticklabels(['Afternoon', 'Evening'])

plt.tight_layout()
plt.show()


# Filter for Saturday
disney_world_sat = disney_world[disney_world['day'] == 'Saturday']
melted_df_sat1 = pd.melt(disney_world_sat, id_vars=['day', 'attraction', 'park'], value_vars=['wait_time_M', 'wait_time_A'], var_name='time_of_day', value_name='wait_time')
melted_df_sat2 = pd.melt(disney_world_sat, id_vars=['day', 'attraction', 'park'], value_vars=['wait_time_A', 'wait_time_E'], var_name='time_of_day', value_name='wait_time')

# combined plots
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Saturday
sns.pointplot(data=melted_df_sat1, x='time_of_day', y='wait_time', hue='park', dodge=True, ax=axes[0])
axes[0].set_title('Saturday Average Wait Times')
axes[0].set_xlabel('Time of Day')
axes[0].set_ylabel('Wait Time')
axes[0].set_xticklabels(['Morning', 'Afternoon'])

# Saturday 2
sns.pointplot(data=melted_df_sat2, x='time_of_day', y='wait_time', hue='park', dodge=True, ax=axes[1])
axes[1].set_title('Saturday Average Wait Times')
axes[1].set_xlabel('Time of Day')
axes[1].set_ylabel('Wait Time')
axes[1].set_xticklabels(['Afternoon', 'Evening'])

plt.tight_layout()
plt.show()


