
import pandas as pd
import os
import sys
import requests
from tabulate import tabulate

# Assuming you have a list of already answered question IDs and answers
answered_questions = []
base_url = 'http://localhost:5002/meeting/questions'

# Specify the patient_id
patient_id = 13403

# Create the full URL with the patient_id parameter
api_url = f'{base_url}?patient_id={patient_id}'

# Perform the GET request
response = requests.get(api_url)


if response.status_code == 200:
    # Extract data from the API response
    answered_questions = response.json().get('data')
    if not answered_questions:
        print("No records found")
        sys.exit(0)
    print("Matching Question Data", answered_questions)

# Define the folder name
folder_name = 'questions'

# Get the current working directory
current_directory = os.getcwd()

# Create the relative folder path by joining the current directory with the folder name
folder_path = os.path.join(current_directory, folder_name)

# Get all files in the folder
all_files = os.listdir(folder_path)

# Filter Excel files based on their extension (.xlsx)
excel_files = [file for file in all_files if file.endswith('.xlsx')]

data_frames = []  # List to store individual DataFrames

# Iterate through each Excel file
for file in excel_files:
    # Read each Excel file
    file_path = os.path.join(folder_path, file)
    data = pd.read_excel(file_path)
    data_frames.append(data)  # Append each DataFrame to the list

# Check if the list of DataFrames is not empty
if data_frames:
    # Concatenate the DataFrames if the list is not empty
    combined_data = pd.concat(data_frames, ignore_index=True)
    
    # Convert the 'question_id' column in combined_data to string data type
    combined_data['question_id'] = combined_data['question_id'].astype(str)
    
    # Convert the list of dictionaries into a DataFrame
    answered_questions_df = pd.DataFrame(answered_questions)

    # Filter the 'combined_data' DataFrame based on 'question_id' and 'question_category' columns
    filtered_combined_data = combined_data.merge(
        answered_questions_df,
        on=['question_id', 'question_category'],
        how='inner'
    )
    
    # Specify the columns you want to display
    selected_columns = ['question_id',  'rca_id', 'impact_id','question_category']

    # Add 'criticalFocus' column based on condition
    filtered_combined_data['criticalFocus'] = filtered_combined_data['criticalFocus'] == 1

    # Extract a subset of rows for the selected columns including the 'criticalFocus' column
    selected_data = filtered_combined_data.loc[:, selected_columns + ['criticalFocus']]

  # Display the selected columns and 'criticalFocus' column using tabulate
    print('Matching Ids')
    print(tabulate(selected_data, headers='keys', tablefmt='pretty'))
      # Convert selected_data['rca_id'] column to a set for faster lookup
    selected_rca_ids = set(selected_data['rca_id'])
    rca_file='rca\RCA to Treatment Goals.xlsx'
    rca_file_path=os.path.join(current_directory, rca_file)
    rca_data = pd.read_excel(rca_file_path)
   # Filter rca_data for matching rca_ids
    matching_rcas = rca_data[rca_data['rca_id'].isin(selected_rca_ids)]

    print("Matching RcA's AND Treatment Goals")
    print(tabulate(matching_rcas, headers='keys', tablefmt='pretty'))
    
    activities_file='activities\Treatment_to_Activities.xlsx'
    activities_file_path=os.path.join(current_directory, activities_file)
    activities_data = pd.read_excel(activities_file_path)
    
    selected_Treatment_Goal_ID = set(matching_rcas['Treatment_Goal_ID'])
    matchingActivities = activities_data[activities_data['Treatment_Goal_ID'].isin(selected_Treatment_Goal_ID)]
    
    print("Matching Activities for Treatment Goals")
    print(tabulate(matchingActivities, headers='keys', tablefmt='pretty'))
    
else:
    print("No data found in Excel files.")
