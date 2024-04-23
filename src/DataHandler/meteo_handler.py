import pandas as pd
import json
import os

# Get the directory of the current Python script
script_dir = os.path.dirname(__file__)
print("Script directory:", script_dir)

# Relative path to the Excel file from the script's directory
relative_excel_path = "TMY_source.xlsx"
print("Relative Excel path:", relative_excel_path)

# Full path to the Excel file by joining the script directory with the relative path
excel_file_path = os.path.join(script_dir, relative_excel_path)
print("Full Excel file path:", excel_file_path)

# Check if the Excel file exists
if not os.path.exists(excel_file_path):
    print("Error: Excel file does not exist.")
    exit()

# Read the Excel file
print("Reading Excel file...")
df = pd.read_excel(excel_file_path)

# Split the DataFrame into chunks of 24 hours
chunks = [df[i:i+24] for i in range(0, len(df), 24)]

# Convert each chunk into a JSON file
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i+1}/{len(chunks)}...")
    # Create a dictionary to hold the JSON data
    json_data = {
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
            "time": [int(pd.Timestamp(dt).timestamp()) for dt in chunk['TIME']],
            "temperature_2m": [float(str(temp).replace(',', '.')) for temp in chunk['Temperature']],
            "shortwave_radiation": [float(str(rad).replace(',', '.')) for rad in chunk['Total_global_horizontal_r']]
        }
    }
    
    # Write the JSON data to a file
    output_file_path = os.path.join(script_dir, '..', 'TestingSequenceMeteo_all', f"day_{i+1}.json")
    print("Writing JSON data to:", output_file_path)
    with open(output_file_path, "w") as f:
        json.dump(json_data, f, indent=2)

print("Script execution completed.")
