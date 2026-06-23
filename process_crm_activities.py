# Create tasks.csv, meeting.csv, calls.csv using cofig_activites

import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import config
import config_activities as config

def format_duration(minutes):
    """Format minutes into HH:MM:SS"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}:00"

def process_data():
    print(f"Loading data from {config.INPUT_FILE}...")
    try:
        df_leads = pd.read_csv(config.INPUT_FILE)
    except FileNotFoundError:
        print(f"Warning: {config.INPUT_FILE} not found. Generating dummy leads data for demonstration.")
        # Dummy data matching expected schema
        df_leads = pd.DataFrame({
            "id": ["L-01", "L-02", "C-03", "L-04"],
            "isConverted": ["Yes", "No", "Yes", "No"],
            "company": ["Acme Corp", "Globex", "Initech", "Soylent"],
            "last name": ["Smith", "Doe", "Lumbergh", "Thorn"]
        })

    # tasks = []
    meetings = []
    calls = []
    
    # Counters for sequential IDs
    # task_counter = 1
    meeting_counter = 1
    call_counter = 1
    
    # Since "no random dates" was requested, we use a deterministic baseline date
    baseline_date = datetime.strptime(config.BASELINE_DATE, "%Y-%m-%d %H:%M:%S")
    for idx, row in df_leads.iterrows():
        # is_converted_str = str(row.get('Converted', '')).strip().lower()
        # is_converted = is_converted_str in ['yes', '1']
        
        # company = row.get('company', '')
        # last_name = row.get('last name', '')
        
        # Determine ID based on conversion status
        # We try to fetch 'contactid' or 'leadid', falling back to 'id', or generating one if missing.
        lead_id = df_leads.at[idx, 'Lead ID']
        task = df_leads.at[idx, 'Subject'] # When generating meetings and calls only
        # Determine counts based on rules
        # if is_converted:
        #     num_tasks = random.randint(1, 4)
        #     # continue  # Skip generating tasks for converted leads as per the new requirement
        # else:
        #     # continue  # Skip generating tasks for unconverted leads as per the new requirement
        #     num_tasks = random.randint(0, 2)
            
        # Generate Tasks
        # fields: subject, due date, status, account name, last name, task id
        # for i in range(num_tasks):
        #     due_date = baseline_date + timedelta(days=idx, hours=i*2)
            
        #     tasks.append({
        #         "Task ID": task_counter,
        #         "Subject": random.choice(config.TASK_SUBJECTS),
        #         "Due Date": due_date.strftime("%d-%m-%Y"),
        #         "Status": random.choice(config.TASK_STATUSES),
        #         "Priority": random.choice(config.TASK_PRIORITIES),
        #         "Lead ID": lead_id
        #     })
        #     task_counter += 1
            
        # Generate Meetings
        # fields: title, meeting venue, from, to, related to, meeting id

        if task == "Meeting":

            start_time = baseline_date + timedelta(days=idx, hours=idx*3)
            end_time = start_time + timedelta(hours=1)
            
            meetings.append({
                "Title": random.choice(config.MEETING_TITLES),
                "Meeting Venue": random.choice(config.MEETING_VENUES),
                "From": start_time.strftime("%d-%m-%Y %I:%M %p"),
                "To": end_time.strftime("%d-%m-%Y %I:%M %p"),
                "Lead ID": lead_id,
                "Meeting ID": meeting_counter
            })
            meeting_counter += 1
        
        else:
            start_time = baseline_date + timedelta(days=idx, hours=idx*4)
            duration_mins = random.choice([5, 15, 30, 45, 60])
            
            calls.append({
                "Call Type": random.choice(config.CALL_TYPES),
                "Start Time": start_time.strftime("%d-%m-%Y %I:%M %p"),
                "Duration": duration_mins,
                "Subject": random.choice(config.CALL_SUBJECTS),
                "Lead ID": lead_id,
                "Call ID": call_counter
            })
            call_counter += 1

    # Save to CSVs. We ensure empty dataframes are created with columns if no records generated
    # df_tasks = pd.DataFrame(tasks, columns=["Task ID","Subject", "Due Date", "Status", "Priority", "Lead ID"])
    df_meetings = pd.DataFrame(meetings, columns=["Title", "Meeting Venue", "From", "To", "Lead ID", "Meeting ID"])
    df_calls = pd.DataFrame(calls, columns=["Call Type", "Start Time", "Duration", "Subject", "Lead ID", "Call ID"])
    
    # print(f"Generated {len(df_tasks)} tasks, saving to {config.TASKS_OUTPUT_FILE}...")
    # df_tasks.to_csv(config.TASKS_OUTPUT_FILE, index=False)
    
    print(f"Generated {len(df_meetings)} meetings, saving to {config.MEETINGS_OUTPUT_FILE}...")
    df_meetings.to_csv(config.MEETINGS_OUTPUT_FILE, index=False)
    
    print(f"Generated {len(df_calls)} calls, saving to {config.CALLS_OUTPUT_FILE}...")
    df_calls.to_csv(config.CALLS_OUTPUT_FILE, index=False)

    print("\nAll relational datasets generated successfully!")

if __name__ == "__main__":
    process_data()
