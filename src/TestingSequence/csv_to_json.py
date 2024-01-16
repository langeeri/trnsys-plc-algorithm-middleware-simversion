import pandas as pd
import os
import json
from datetime import datetime

# Get the path to the current script's directory
script_directory = os.path.dirname(os.path.realpath(__file__))

# Specify the CSV file path
csv_file_path = os.path.join(script_directory, 'case_varPrice_Hday_3.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Convert the 'h' column to datetime format
df['h'] = pd.to_datetime(df['h'], format='%H').dt.hour

# Group by the 'h' column and calculate the mean for each hour
mean_values = df.groupby('h')['Ta', 'G_Gcs'].mean()

# Round the values to a maximum of four decimal places
mean_values_rounded = mean_values.round(4)

# Convert the 'time' values to Unix timestamp
mean_values_rounded['time_unix'] = mean_values_rounded.index.map(lambda x: int(datetime(2023, 1, 1, x).timestamp()))

# Convert the result to a JSON format
result_json = {
    "latitude": 50.08,
    "longitude": 14.419998,
    "generationtime_ms": 0.03993511199951172,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 205.0,
    "hourly_units": {
        "time": "unixtime",
        "temperature_2m": "\u00b0C",
        "shortwave_radiation": "W/m\u00b2"
    },
    "hourly": {
        "time": mean_values_rounded['time_unix'].tolist(),  # Convert index to list
        "temperature_2m": mean_values_rounded['Ta'].tolist(),  # Convert column to list
        "shortwave_radiation": mean_values_rounded['G_Gcs'].tolist()  # Convert column to list
    }
}

# Specify the output file path
output_file_path = os.path.join(script_directory, 'case_varPrice_Hday_3_hourly_meteo.json')

# Write the formatted JSON to the output file
with open(output_file_path, 'w') as output_file:
    json.dump(result_json, output_file, indent=2)

# Display a message
print(f"Formatted JSON has been written to: {output_file_path}")
