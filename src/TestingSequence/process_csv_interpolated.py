import csv
import os

# Get the directory where the script is located
script_directory = os.path.dirname(__file__)
print(f"Script directory: {script_directory}")

# Get a list of all files in the script directory
files = os.listdir(script_directory)

# Columns to skip
columns_to_skip = ['m', 'dm', 'dy', 'h', 'mi']

# Process each file in the directory
for file_name in files:
    print(f"Checking file: {file_name}")
    # Check if the file is a CSV file
    if file_name.endswith('.csv'):
        print(f"Processing file: {file_name}")
        # Read the CSV file
        with open(os.path.join(script_directory, file_name), 'r') as file:
            reader = csv.reader(file)
            data = list(reader)

        # Skip the header row
        header = data[0]
        data = data[1:]

        # Determine indices of columns to keep
        columns_to_keep = [i for i, col_name in enumerate(header) if col_name not in columns_to_skip]

        # Initialize variables to store hourly aggregated data
        hourly_data = []
        current_hour_data = None
        current_hour_values = []

        # Loop through the data and aggregate over each hour
        for row in data:
            hour = int(row[4])
            if current_hour_data is None or hour != current_hour_data:
                # If it's a new hour, calculate the average for the previous hour
                if current_hour_data is not None:
                    # Calculate the average of each column for the previous hour
                    average_values = [sum(float(hour_data[i]) for hour_data in current_hour_values) / len(current_hour_values) for i in columns_to_keep]
                    hourly_data.append([row[0], row[1], row[2], row[3], current_hour_data, '0'] + average_values)
                
                # Start a new hour
                current_hour_data = hour
                current_hour_values = [row]
            else:
                # Add the row to the current hour's data
                current_hour_values.append(row)

        # Write the hourly interpolated data to a new CSV file
        output_file = os.path.join(script_directory, os.path.splitext(file_name)[0] + '_hourly_interpolated.csv')
        print(f"Writing hourly interpolated data to: {output_file}")
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow([header[i] for i in columns_to_keep])
            # Write the hourly interpolated data
            writer.writerows(hourly_data)
