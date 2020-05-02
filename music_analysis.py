import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(color_codes=True)

#Spotify Credentials
clientid = 'spotify_client_id'
secret = 'spotify_client_secret'

client_credentials_manager = SpotifyClientCredentials(client_id = clientid, client_secret = secret)

#Initialise Spotify API
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Functions
def get_tracks_features(playlist_id):
    
    '''
    Function to take a playlist_id as input and return a dataframe consisting with songs, artists, albums and audio features. 

    '''

    # Retrieve songs from the playlist    
    response = sp.playlist_tracks(playlist_id)
    tracks = response['items']
    
    #Loop to retrieve all songs 
    
    while response['next']:
        response = sp.next(response)
        tracks.extend(response['items']) 
        
    #initialise lists
    artists, albums, track_ids, track_names = [], [], [], []
    for i in range(len(tracks)):
        
        #add try except here
        try:
            artist = tracks[i]['track']['artists'][0]['name']
        except:
            artist = 'Not Available'
        artists.append(artist)
        
        try:
            album = tracks[i]['track']['album']['name']
        except:
            album = 'Not Available'
        albums.append(album)
        
        try:
            track_id = tracks[i]['track']['id']
        except:
            track_id = 'Not Available'
        track_ids.append(track_id)
        
        try:
            track_name = tracks[i]['track']['name']
        except:
            track_name = 'Not Available'
        track_names.append(track_name)
        
    #create  a dataframe 
    tracks_df = pd.DataFrame({'artist' : artists, 'album' : albums, 'track_id' : track_ids, 'track_name' : track_names})
    
    track_audio_features = []
         
    loop_length = len(track_ids)
    
    #loop by 100 because audio_features has a limit of 100 songs
    for i in range(0, loop_length, 100):
        temp_track_id_list = track_ids[i:i+100]
        af_response = sp.audio_features(tracks = temp_track_id_list)
        i += 100
        track_audio_features.extend(af_response)
        
    track_audio_features = [i for i in track_audio_features if i is not None]
    
    audio_features_df = pd.DataFrame(track_audio_features)
    
    #merge the two dataframes and return
    main_df = pd.merge(tracks_df, audio_features_df, how = 'inner', left_on = ['track_id'],  right_on = ['id'])
    main_df['duration_ms'] = pd.to_numeric(main_df['duration_ms'])
        

    return main_df

def mean_feature_playlist(main_df, playlist_name):
    
    '''
    Function that takes the dataframe from get_tracks_features and playlist_name to return means of audio features for different playlists.

    '''
    main_df_means = pd.DataFrame(main_df.mean()).reset_index(drop = False)
    main_df_means.columns = ['audio_feature', 'value']
    main_df_means = main_df_means[(main_df_means['audio_feature'] == 'danceability') | (main_df_means['audio_feature'] == 'energy') |(main_df_means['audio_feature'] == 'speechiness') | (main_df_means['audio_feature'] == 'acousticness') | (main_df_means['audio_feature'] == 'instrumentalness') | (main_df_means['audio_feature'] == 'valence')]
    main_df_means['playlist'] = playlist_name

    return main_df_means

def append_all_dataframes(df1, df2, df3, df4, df5):
    
    '''
    Function to append dataframes to each other. 5 dataframes for 5 playlist of the time of day.

    '''

    final_df = pd.DataFrame()
    final_df = final_df.append(df1)
    final_df = final_df.append(df2)
    final_df = final_df.append(df3)
    final_df = final_df.append(df4)
    final_df = final_df.append(df5)

    return final_df

def tracks_by_time(id1, id2, id3, id4, id5):
    '''
    Function to get data for all playlists

    '''
    
    main_df_1 = get_tracks_features(id1)
    main_df_2 = get_tracks_features(id2)
    main_df_3 = get_tracks_features(id3)
    main_df_4 = get_tracks_features(id4)
    main_df_5 = get_tracks_features(id5)
    
    main_df = append_all_dataframes(main_df_1, main_df_2, main_df_3, main_df_4, main_df_5)

    return main_df

# Retrieve data for all playlists
morning_track_df = tracks_by_time('37i9dQZF1DWSWyJydK4fTU', '37i9dQZF1DXc5e2bJhV6pu', '37i9dQZF1DX2MyUCsl25eb', '37i9dQZF1DWWLToO3EeTtX', '37i9dQZF1DXdd3gw5QVjt9')
morning_track_df['playlist'] = 'Morning'
morning_mean_df = mean_feature_playlist(morning_track_df, 'Morning')

workout_track_df = tracks_by_time('37i9dQZF1DWSJHnPb1f0X3', '37i9dQZF1DWUVpAXiEPK8P', '37i9dQZF1DX70RN3TfWWJh', '37i9dQZF1DXdxcBWuJkbcy', '37i9dQZF1DX76Wlfdnj7AP')
workout_track_df['playlist'] = 'Workout'
workout_mean_df = mean_feature_playlist(workout_track_df, 'Workout')

work_track_df = tracks_by_time('37i9dQZF1DWT5lkChsPmpy', '37i9dQZF1DWSluGMsH1R9r', '37i9dQZF1DX3PFzdbtx1Us', '37i9dQZF1DWZeKCadgRdKQ', '37i9dQZF1DWXLeA8Omikj7')
work_track_df['playlist'] = 'Work'
work_mean_df = mean_feature_playlist(work_track_df, 'Work')

evening_track_df = tracks_by_time('37i9dQZF1DXaX7xgI3f7y8', '37i9dQZF1DWXSyfX6gqDNp', '37i9dQZF1DX3bSdu6sAEDF', '37i9dQZF1DWZ0OzPeadl0h', '37i9dQZF1DXcWBRiUaG3o5')
evening_track_df['playlist'] = 'Evening'
evening_mean_df = mean_feature_playlist(evening_track_df, 'Evening')

cooking_track_df = tracks_by_time('37i9dQZF1DXcwwDgVA4D78', '37i9dQZF1DWUQaB5AfW9Oa', '37i9dQZF1DX9pQ3JDTosFG', '37i9dQZF1DX2B3xivNXPeb', '37i9dQZF1DX2FsCLsHeMrM')
cooking_track_df['playlist'] = 'Cooking'
cooking_mean_df = mean_feature_playlist(cooking_track_df, 'Cooking')

dinner_track_df = tracks_by_time('37i9dQZF1DX6kz6Kli3wib', '37i9dQZF1DWTALrdBtcXjw', '37i9dQZF1DXbm6HfkbMtFZ', '37i9dQZF1DXatMjChPKgBk', '37i9dQZF1DX4xuWVBs4FgJ')
dinner_track_df['playlist'] = 'Dinner'
dinner_mean_df = mean_feature_playlist(dinner_track_df, 'Dinner')

night_track_df = tracks_by_time('37i9dQZF1DXea80XwOJRgD', '37i9dQZF1DX7ZnTv0GKubq', '37i9dQZF1DXdQvOLqzNHSW', '37i9dQZF1DX6GJXiuZRisr', '37i9dQZF1DX4wta20PHgwo')
night_track_df['playlist'] = 'Night'
night_mean_df = mean_feature_playlist(night_track_df, 'Night')

sleep_track_df = tracks_by_time('37i9dQZF1DWSiZVO2J6WeI', '37i9dQZF1DWUKPeBypcpcP', '37i9dQZF1DXa1rZf8gLhyz', '37i9dQZF1DXbcPC6Vvqudd', '37i9dQZF1DWZd79rJ6a7lp')
sleep_track_df['playlist'] = 'Sleep'
sleep_mean_df = mean_feature_playlist(sleep_track_df, 'Sleep')


final_df = pd.DataFrame()
final_df = final_df.append(morning_mean_df)
final_df = final_df.append(workout_mean_df)
final_df = final_df.append(work_mean_df)
final_df = final_df.append(evening_mean_df)
final_df = final_df.append(cooking_mean_df)
final_df = final_df.append(dinner_mean_df)
final_df = final_df.append(night_mean_df)
final_df = final_df.append(sleep_mean_df)

# Retrieve my playlists and data

# Lo Fi Beats
my_morning_track_df = get_tracks_features('37i9dQZF1DWWQRwui0ExPn')
my_morning_track_df['playlist'] = 'My Morning'
my_morning_mean_df = mean_feature_playlist(my_morning_track_df, 'My Morning')

# MKBHD Videos
my_workout_track_df = get_tracks_features('0ZXVX604hmghJgqWCMsqcU')
my_workout_track_df['playlist'] = 'My Workout'
my_workout_mean_df = mean_feature_playlist(my_workout_track_df, 'My Workout')

# Lowkey Tech
my_work_track_df = get_tracks_features('37i9dQZF1DX0r3x8OtiwEM')
my_work_track_df['playlist'] = 'My Work'
my_work_mean_df = mean_feature_playlist(my_work_track_df, 'My Work')

# Ultimate Indie
my_evening_track_df = get_tracks_features('37i9dQZF1DX2Nc3B70tvx0')
my_evening_track_df['playlist'] = 'My Evening'
my_evening_mean_df = mean_feature_playlist(my_evening_track_df, 'My Evening')

# Legendary Guitar Solos
my_cooking_track_df = get_tracks_features('37i9dQZF1DWSlJG7YPUBHF')
my_cooking_track_df['playlist'] = 'My Cooking'
my_cooking_mean_df = mean_feature_playlist(my_cooking_track_df, 'My Cooking')

# Soulful Dinner
my_dinner_track_df = get_tracks_features('37i9dQZF1DWZheHO7xislj')
my_dinner_track_df['playlist'] = 'My Dinner'
my_dinner_mean_df = mean_feature_playlist(my_dinner_track_df, 'My Dinner')

# Deep House Relax
my_night_track_df = get_tracks_features('37i9dQZF1DX2TRYkJECvfC')
my_night_track_df['playlist'] = 'My Night'
my_night_mean_df = mean_feature_playlist(my_night_track_df, 'My Night')

# Analysis
my_sleep_track_df = get_tracks_features('3oDrqmwucKIKFqcTMjewtR')
my_sleep_track_df['playlist'] = 'My Sleep'
my_sleep_mean_df = mean_feature_playlist(my_sleep_track_df, 'My Sleep')

# Faceted Radar Charts
radar_df = pd.DataFrame()

def convert_to_radar_df(mean_df):
    mean_df_pivot = mean_df.pivot_table(mean_df, index = 'playlist', columns = 'audio_feature').reset_index()
    mean_df_pivot.columns = ['playlist', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'valence']
    
    return mean_df_pivot

for dataframe in (morning_mean_df, workout_mean_df, work_mean_df, evening_mean_df, cooking_mean_df, dinner_mean_df, night_mean_df, sleep_mean_df):
    temp_radar_df = convert_to_radar_df(dataframe)
    radar_df = radar_df.append(temp_radar_df)

radar_df = radar_df.reset_index(drop = True)

radar_df = radar_df[['playlist', 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']]

def make_spider(row, title, color):
    
    categories = list(radar_df)[1:]
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax = plt.subplot(3,3,row+1, polar=True, )
     
    ax.set_theta_offset(np.pi / 2)

    plt.xticks(angles[:-1], categories, color = 'grey', size=8)
    
    ax.set_theta_zero_location('N')

    plt.ylim(0,1)
    
    plt.yticks(size = 8)

    values = radar_df.loc[row].drop('playlist').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, 'o-', color = color, linewidth = 0.75, linestyle = 'solid', markersize = 4)
    ax.fill(angles, values, color = color, alpha = 0.1)
    
    # Add a title
    plt.title(title, size = 11, color = color, y = 1.1)   

my_dpi=96
plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)

my_palette = plt.cm.get_cmap("Set2", len(radar_df.index))
 
# Loop to plot
for row in range(0, len(radar_df.index)):
    make_spider( row = row, title = radar_df['playlist'][row], color = my_palette(row))

    plt.tight_layout()


# Faceted Multivariable Radar Charts

my_radar_df = pd.DataFrame()

for dataframe in (my_morning_mean_df, my_workout_mean_df, my_work_mean_df, my_evening_mean_df, my_cooking_mean_df, my_dinner_mean_df, my_night_mean_df, my_sleep_mean_df):
    temp_radar_df = convert_to_radar_df(dataframe)
    my_radar_df = my_radar_df.append(temp_radar_df)

my_radar_df = my_radar_df.reset_index(drop = True)

my_radar_df = my_radar_df[['playlist', 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']]

def make_spider_two_variable(row, title, color):
    
    categories = list(radar_df)[1:]
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax = plt.subplot(3,3,row+1, polar=True, )
     
    ax.set_theta_offset(np.pi / 2)

    plt.xticks(angles[:-1], categories, color = 'grey', size=8)
    
    ax.set_theta_zero_location('N')

    plt.ylim(0,1)
    
    plt.yticks(size = 8)

    values = radar_df.loc[row].drop('playlist').values.flatten().tolist()
    values += values[:1]
    
    values2 = my_radar_df.loc[row].drop('playlist').values.flatten().tolist()
    values2 += values2[:1]
    
    ax.plot(angles, values, 'o-', color = 'red', linewidth = 0.75, linestyle = 'solid', markersize = 4)
    ax.fill(angles, values, color = 'red', alpha = 0.1)
    
    ax.plot(angles, values2, 'o-', color = 'blue', linewidth = 0.75, linestyle = 'solid', markersize = 4)
    ax.fill(angles, values2, color = 'blue', alpha = 0.1)
    
    ax.legend()
    # Add a title
    plt.title(title, size = 11, color = color, y = 1.1)   

my_dpi=96
plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)

my_palette = plt.cm.get_cmap("Set2", len(radar_df.index))

# Loop to plot
for row in range(0, len(radar_df.index)):
    make_spider_two_variable( row = row, title = radar_df['playlist'][row], color = my_palette(row))

    plt.tight_layout()
    plt.legend(loc="upper left")


# Correlation dataframe and plot
def corr_matrix(dataframe):
    temp_df = dataframe[['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']]
    corr_df = temp_df.corr()
    
    return corr_df

corr_df = corr_matrix(final_df)

sns.heatmap(corr_df, linewidths = 0.5, cmap = "coolwarm", vmin = -1, annot = True) 
