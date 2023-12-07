from flask import Flask, jsonify
import pandas as pd
import os
import requests
from tabulate import tabulate
import json
app = Flask(__name__)

@app.route('/process_data/<int:patient_id>', methods=['GET'])
def process_data(patient_id):
    answered_questions = []
    base_url = 'http://localhost:5002/meeting/questions'
    api_url = f'{base_url}?patient_id={patient_id}'
    response = requests.get(api_url)

    if response.status_code == 200:
        answered_questions = response.json().get('data')
        if not answered_questions:
            return jsonify({"message": "No records found"})
    
    folder_name = 'questions'
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, folder_name)
    all_files = os.listdir(folder_path)
    excel_files = [file for file in all_files if file.endswith('.xlsx')]
    data_frames = []

    for file in excel_files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_excel(file_path)
        data_frames.append(data)

    if data_frames:
        combined_data = pd.concat(data_frames, ignore_index=True)
        combined_data['question_id'] = combined_data['question_id'].astype(str)
        answered_questions_df = pd.DataFrame(answered_questions)
        filtered_combined_data = combined_data.merge(
            answered_questions_df,
            on=['question_id', 'question_category'],
            how='inner'
        )
        selected_columns = ['question_id', 'rca_id', 'impact_id', 'question_category']
        filtered_combined_data['criticalFocus'] = filtered_combined_data['criticalFocus'] == 1
        selected_data = filtered_combined_data.loc[:, selected_columns + ['criticalFocus']]

        selected_rca_ids = set(selected_data['rca_id'])
        rca_file = 'rca\RCA to Treatment Goals.xlsx'
        rca_file_path = os.path.join(current_directory, rca_file)
        rca_data = pd.read_excel(rca_file_path)
        matching_rcas = rca_data[rca_data['rca_id'].isin(selected_rca_ids)]

        activities_file = 'activities\Treatment_to_Activities.xlsx'
        activities_file_path = os.path.join(current_directory, activities_file)
        activities_data = pd.read_excel(activities_file_path)

        selected_Treatment_Goal_ID = set(matching_rcas['Treatment_Goal_ID'])
        matchingActivities = activities_data[activities_data['Treatment_Goal_ID'].isin(selected_Treatment_Goal_ID)]
        # Display the selected columns and 'criticalFocus' column using tabulate
        print('Matching Ids')
        print(tabulate(selected_data, headers='keys', tablefmt='pretty'))
        
        
        print("Matching RcA's AND Treatment Goals")
        print(tabulate(matching_rcas, headers='keys', tablefmt='pretty'))
        print("Matching Activities for Treatment Goals")
        print(tabulate(matchingActivities, headers='keys', tablefmt='pretty'))
        
        selected_data_json_string = selected_data.to_json(orient='records')
        matching_rcasa_json_string = matching_rcas.to_json(orient='records')
        matchingActivities_json_string = matchingActivities.to_json(orient='records')


        selected_data_json_data = json.loads(selected_data_json_string)
        matching_rcasa_data_json_data = json.loads(matching_rcasa_json_string)
        matchingActivities_json_data = json.loads(matchingActivities_json_string)
        result = {
            "Matching Ids": selected_data_json_data,
            "Matching RcA's AND Treatment Goals":matching_rcasa_data_json_data,
            "Matching Activities for Treatment Goals":matchingActivities_json_data
        }

        return jsonify(result)
    else:
        return jsonify({"message": "No data found in Excel files."})

if __name__ == '__main__':
    app.run(debug=True)
