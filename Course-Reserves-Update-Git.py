import requests, json, time
import pandas as pd

# Open csv file listing representations
csv_file_path = "CSV FILE PATH HERE"
d = pd.read_csv(csv_file_path)
d.set_index("mms_id", inplace=True, drop=True)

# API endpoint URL
apicall = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/representations/{rep_id}?format=json&apikey={api_key}'

# API key
api_key = 'YOUR API KEY HERE'

# API Headers
headers = {
    "Authorization": f"apikey {api_key}",
    "Content-Type": "application/json"
}

# Iterate update process over list of representations
for index, row in d.iterrows():

    # Set up each representation's MMSID and Representation ID for the API URL
    mms_id = index
    rep_id = row['rep_id']
    print(mms_id)
    print(rep_id)

    # Make the API call, printing the URL first for inspection
    print(apicall.format(mms_id=mms_id, rep_id=rep_id, api_key=api_key))
    response = requests.get(apicall.format(mms_id=mms_id, rep_id=rep_id, api_key=api_key), headers=headers)
    print(response)

    # Check the response status
    if response.status_code == 200:

        # API call successful:

        #Pull the representation data into a dictionary from JSON, then print it for inspection
        rep_data = response.json()
        print("First Call: " + str(rep_data))

        #Update the CSV to show the representation's current status
        d.loc[mms_id, 'initial_status'] = rep_data['active']['desc']

        #Change the representation data dictionary to update its status, then print for inspection
        rep_data['active']['value'] = "false"
        rep_data['active']['desc'] = "Inactive"
        print("Corrected JSON: " + str(rep_data))

        #Push the updated dictionary back to Alma as JSON
        update = requests.put(apicall.format(mms_id=mms_id, rep_id=rep_id, api_key=api_key), headers=headers, data=json.dumps(rep_data))
        updated_data = update.json()
        print("Update Response: " + str(updated_data))

        #Wait a few seconds for the update, then retrieve the representation's data again as JSON to check it
        time.sleep(3)
        check_response = requests.get(apicall.format(mms_id=str(mms_id), rep_id=str(rep_id), api_key=api_key))
        new_data = check_response.json()
        print("Check Call: " + str(new_data) + "\n")

        #Update the CSV with the new, checked data
        d.loc[index, 'checked_status'] = rep_data['active']['desc']
        d.loc[index, 'status'] = "Updated"

        #Save the CSV file. Set the data type as "string" to prevent rounding of MMSID and Representation ID
        d = d.astype(str)
        d.to_csv(csv_file_path)

    else:
        # API call failed
        print('API call failed with status code {}'.format(response.status_code))

        #Update the CSV to indicate the failed API call
        d.loc[index, 'status'] = "Error"
        d.to_csv(csv_file_path)
