"""
Configuration file for CRM data generation (Tasks, Meetings, Calls).
"""

INPUT_FILE = "data/tasks_leads.csv"

# Output files
# TASKS_OUTPUT_FILE = "tasks_leads.csv"
MEETINGS_OUTPUT_FILE = "data/meeting_contacts.csv"
# CALLS_OUTPUT_FILE = "data/calls_leads.csv"

# Configuration for Tasks
# TASK_STATUSES = ["Not Started", "Deferred", "In Progress", "Completed", "Waiting for input"]
# TASK_SUBJECTS = ["Email", "Call", "Meeting", "Send Letter", "Product Demo"]
# TASK_PRIORITIES = ["High", "Highest", "Low", "Lowest", "Normal"]

# Configuration for Meetings
MEETING_VENUES = ["Client location", "In-office"]
MEETING_TITLES = ["Initial Discovery Call", "Product Demo", "Technical Deep Dive", "Pricing Discussion", "Contract Negotiation"]

# Configuration for Calls
# CALL_TYPES = ["Outbound", "Inbound", "Missed"]
# CALL_SUBJECTS = ["Cold Outreach", "Follow-up", "Support Inquiry", "Billing Question", "Check-in"]

# Baseline date to use (since random dates are disabled, we generate structured sequential dates)
BASELINE_DATE = "2023-10-01 09:00:00"
