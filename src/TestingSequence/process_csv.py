import csv
import os
import xlsxwriter

# Get the directory where the script is located
script_directory = os.path.dirname(__file__)
print(f"Script directory: {script_directory}")

# Get a list of all files in the script directory
files = os.listdir(script_directory)

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

        # Filter data to select only rows where the minute is 0
        hourly_data = [row for row in data if int(row[5]) == 0]

        # Write the hourly data to a new Excel file
        output_file = os.path.join(script_directory, os.path.splitext(file_name)[0] + '_hourly.xlsx')
        print(f"Writing hourly data to: {output_file}")
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet()
        
        # Write the header row
        for col, value in enumerate(header):
            worksheet.write(0, col, value)

        # Write the hourly data
        for row_num, row_data in enumerate(hourly_data):
            for col_num, value in enumerate(row_data):
                worksheet.write(row_num + 1, col_num, value)

        workbook.close()
