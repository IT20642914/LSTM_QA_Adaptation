import pandas as pd
from tabulate import tabulate
import os

# Assuming you have a list of already answered question IDs and answers
answered_questions = [
    {'question_id': 2, 'answer': 'External_Image'},
    {'question_id': 4, 'answer': 'Health_Fitness'},
    # Add more question IDs and answers as needed
]

# Define the folder name
folder_name = 'quections'

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

    # Extract question IDs from the list
    question_ids = [q['question_id'] for q in answered_questions]

    # Filter the combined DataFrame based on the specified question IDs and 'redFlag_option'
    filtered_data = combined_data[
        (combined_data['question_id'].isin(question_ids)) &
        (combined_data['redFlag_option'].isin([q['answer'] for q in answered_questions]))
    ]

    # Specify the columns you want to display
    selected_columns = ['question_id', 'question', 'choice_options', 'redFlag_option', 'rca_id', 'impact_id']

    # Add 'criticalFocus' column based on condition
    filtered_data['criticalFocus'] = filtered_data['criticalFocus'] == 1

    # Extract a subset of rows for the selected columns including the 'criticalFocus' column
    selected_data = filtered_data.loc[:, selected_columns + ['criticalFocus']]
    # Convert selected_data['rca_id'] column to a set for faster lookup
    selected_rca_ids = set(selected_data['rca_id'])
    # Display the selected columns and 'criticalFocus' column using tabulate
    print("Matching Question Data")
    print(tabulate(selected_data, headers='keys', tablefmt='pretty'))
    
    rca_file='rca\RCA to Treatment Goals.xlsx'
    rca_file_path=os.path.join(current_directory, rca_file)
    rca_data = pd.read_excel(rca_file_path)
   # Filter rca_data for matching rca_ids
    matching_rcas = rca_data[rca_data['rca_id'].isin(selected_rca_ids)]

    print("Matching RcA's")
    print(tabulate(matching_rcas, headers='keys', tablefmt='pretty'))
    
    activities_file='activities\Treatment_to_Activities.xlsx'
    activities_file_path=os.path.join(current_directory, activities_file)
    activities_data = pd.read_excel(activities_file_path)
 
    selected_Treatment_Goal_ID = set(matching_rcas['Treatment_Goal_ID'])
    matchingActivities = activities_data[activities_data['Treatment_Goal_ID'].isin(selected_Treatment_Goal_ID)]
    
    print("Matching Activities")
    print(tabulate(matchingActivities, headers='keys', tablefmt='pretty'))
else:
    print("No data found in Excel files.")
