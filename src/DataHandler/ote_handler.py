import pandas as pd
import json
import os

# Get the directory of the current Python script
script_dir = os.path.dirname(__file__)
print("Script directory:", script_dir)

# Relative path to the Excel file from the script's directory
relative_excel_path = "OTE_source.xlsx"
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
chunks = [df.iloc[i:i+24] for i in range(0, len(df), 24)]

# Iterate over each chunk (each representing 24 hours of data)
for i, chunk in enumerate(chunks):
    # Create a dictionary to hold the JSON data for this chunk
    json_data = {
        "axis": {
            "x": {
                "decimals": 0,
                "legend": "Hour",
                "short": False,
                "step": 1
            },
            "y": {
                "decimals": 0,
                "legend": "Price (EUR/MWh)",
                "step": 4,
                "tooltip": "Price (EUR/MWh)"
            },
            "y2": {
                "decimals": 0,
                "legend": "Volume (MWh)",
                "step": 4,
                "tooltip": "Volume (MWh)"
            }
        },
        "data": {
            "dataLine": [
                {
                    "bold": False,
                    "colour": "FF6600",
                    "point": [{"x": str(hour + 1), "y": 0} for hour in range(24)],
                    "title": "Volume (MWh)",
                    "tooltip": "Volume",
                    "tooltipDecimalsY": 1,
                    "type": "2",
                    "useTooltip": True,
                    "useY2": True
                },
                {
                    "bold": False,
                    "colour": "A04000",
                    "point": [{"x": str(hour + 1), "y": float(row['el_spot'])} for hour, row in chunk.iterrows()],
                    "title": "Price (EUR/MWh)",
                    "tooltip": "Price",
                    "tooltipDecimalsY": 2,
                    "type": "1",
                    "useTooltip": True,
                    "useY2": False
                }
            ]
        },
        "graph": {
            "fullscreen": True,
            "title": f"Day-Ahead Market Results - chunk_{i}",
            "zoom": True
        }
    }


    # Write the JSON data to a file
    output_file_path = os.path.join(script_dir, '..', 'TestingSequenceOTE_all', f"day_{i+1}.json")
    with open(output_file_path, "w") as f:
        json.dump(json_data, f, indent=2)

print("Conversion to JSON completed.")
