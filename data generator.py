import pandas as pd
import random
import numpy as np
import datetime as dt
from datetime import timedelta


def generate_dataset(name):
    astronaut_ids = [i for i in range(1, 19)]

    # define start and end time of the period
    start_date = dt.datetime(2022, 1, 1)
    end_date = dt.datetime(2022, 12, 31)

    # define the activity info
    activity_info = {
        'sleep1': {'room': 5, 'oxygen_consumption': 0.0067, "start": dt.time(0), "end": dt.time(6), "duration": 6},
        'walk': {'room': 4, 'oxygen_consumption': 0.0083, "start": dt.time(6), "end": dt.time(7), "duration": 1},
        'eat': {'room': 1, 'oxygen_consumption': 0.0083, "start": dt.time(7), "end": dt.time(9), "duration": 2},
        'work': {'room': 2, 'oxygen_consumption': 0.0083, "start": dt.time(9), "end": dt.time(16), "duration": 7},
        'sport': {'room': 3, 'oxygen_consumption': 0.0133, "start": dt.time(16), "end": dt.time(18), "duration": 2},
        'rest': {'room': 4, 'oxygen_consumption': 0.0083, "start": dt.time(18), "end": dt.time(22), "duration": 4},
        'sleep': {'room': 5, 'oxygen_consumption': 0.0067, "start": dt.time(22), "end": dt.time(0), "duration": 2}
    }

    features = [
        "astronaut_id",
        "room_id",
        "start_timestamp",
        "end_timestamp",
        "activity",
        "oxygen_consumption"]
    # Initialize the dataset list
    dataset = []
    frameset = []

    # Loop through each day in the month
    for date in (start_date + dt.timedelta(n) for n in range((end_date - start_date).days)):
        # Loop through each person
        for person in astronaut_ids:
            current_hours = 0
            # Loop through each hour of the day
            while current_hours < 24:
                # Get the current timestamp
                timestamp = dt.datetime.combine(date, dt.time(current_hours))
                # Initialize the activity and its duration
                activity = None
                room_id = None
                oxygen_consumption = None
                duration = None
                time_hour = timestamp.time().hour
                # Loop through each activity and check if it can be done during this hour
                for name, data in activity_info.items():
                    if data["end"].hour == 0:
                        end_hour = 24
                    else:
                        end_hour = data["end"].hour
                    if data["start"].hour == time_hour:
                        # Assign the activity and its duration
                        activity = name
                        room_id = data["room"]
                        oxygen_consumption = data["oxygen_consumption"]
                        duration = data["duration"]
                        start = date + timedelta(hours=data["start"].hour, minutes=data["start"].minute,
                                                 seconds=data["start"].second)
                        if data["end"].hour == 0:
                            end = date + timedelta(days=1, hours=data["end"].hour, minutes=data["end"].minute,
                                                   seconds=data["end"].second)
                        else:
                            end = date + timedelta(hours=data["end"].hour, minutes=data["end"].minute,
                                                   seconds=data["end"].second)
                        break
                # Add the activity and its duration to the dataset
                if activity is not None:
                    dataset.append((person, activity, start, end, room_id, oxygen_consumption))

                    current_hours = current_hours + duration

                    frameset.append([person, room_id, start, end, activity, oxygen_consumption])

    # Sort the dataset by astronaut and start timestamp
    dataset.sort(key=lambda x: (x[0], x[2]))

    df = pd.DataFrame(frameset, columns=features)
    df = df.drop_duplicates()
    df = df.replace({'sleep1': 'sleep'})
    df.to_csv('data_clean.csv', index=False)

    # DEVIATIONS

    # Define a function to adjust the activities with deviations in duration and recalculate the start and end times
    def adjust_activities(df):
        # Group the data by astronaut_id and date
        df['date'] = pd.to_datetime(df['start_timestamp']).dt.date
        grouped = df.groupby(['astronaut_id', 'date'])

        # Loop through each group and adjust the activities
        for group, data in grouped:
            # Calculate the total duration of all activities for the day

            total_duration = (data['end_timestamp'] - data['start_timestamp']).sum().total_seconds() / 60

            # Loop through each activity and adjust the duration
            for i, row in data.iterrows():
                # Get the current duration of the activity
                current_duration = (row['end_timestamp'] - row['start_timestamp']).total_seconds() / 60

                # Generate a random deviation for the activity duration
                random_deviation = random.choice([-40, -20, 20, 40])

                # Calculate the new duration for the activity
                new_duration = current_duration + random_deviation

                # Make sure the new duration is not negative or greater than the total duration for the day
                if new_duration < 0:
                    new_duration = 0
                elif new_duration > total_duration:
                    new_duration = total_duration

                # Calculate the new end time for the activity
                if row['end_timestamp'].hour == 0:
                    new_end_time = row['end_timestamp']
                else:
                    new_end_time = row['start_timestamp'] + pd.Timedelta(minutes=new_duration)
                # Update the end time of the activity in the dataframe
                df.at[i, 'end_timestamp'] = new_end_time
                # Update the start time of the next activity in the dataframe
                try:
                    if df.at[i + 1, 'start_timestamp'].hour != 0 and new_end_time != row['end_timestamp']:
                        df.at[i+1, 'start_timestamp'] = df.at[i+1, 'start_timestamp']+pd.Timedelta(minutes=random_deviation)
                except KeyError:
                    break

        # Remove the date column from the dataframe
        df = df.drop('date', axis=1)

        # Return the adjusted dataframe
        return df

    # Call the adjust_activities function on the original dataframe
    adjusted_df = adjust_activities(df)

    adjusted_df.to_csv('data_20_40_min_deviations.csv', index=False)


if __name__ == '__main__':
    generate_dataset('PyCharm')
