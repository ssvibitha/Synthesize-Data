"""
Configuration file for CRM data generation (Tasks, Meetings, Calls).
"""
import datetime
INPUT_FILE = "data/Invoices_new.csv"
# INPUT_FILE = "data/new_leads.csv"

# Output files
OUTPUT_FILE = "data/Invoices_new.csv"
# TASKS_OUTPUT_FILE = "data/tasks_9000.csv"
# MEETINGS_OUTPUT_FILE = "data/meeting_9000.csv"
# CALLS_OUTPUT_FILE = "data/calls_9000.csv"

# Configuration for quotes
# QUOTE_SUBJECTS = ["Annual Software License",
#     "CRM Implementation",
#     "Support Package",
#     "Cloud Migration",
#     "Training Services",
#     "Product Purchase",
#     "Infrastructure Upgrade",
#     "Consulting Services"]

# Configuration for Case
CASE_TITLE=["Unable to Access Dashboard","Data Synchronization Error","API Integration Failure",
            "Refund Request","Payment Not Reflected","Account Access Request","Password Reset Assistance","Quote Revision Request",
            "Order Cancellation Request","New Integration Requirement","Configuration Assistance"]
CASE_STATUS=["Resolved","In Progress","Active"]
CASE_ORIGIN=["Email","Phone","Web","Chat"]

# Configuration for Tasks
# TASK_STATUSES = ["Not Started", "Deferred", "In Progress", "Completed", "Waiting for input"]
# TASK_SUBJECTS = ["Email", "Call", "Meeting", "Send Letter", "Product Demo"]
# TASK_PRIORITIES = ["High", "Highest", "Low", "Lowest", "Normal"]

# Configuration for Meetings
# MEETING_VENUES = ["Client location", "In-office"]
# MEETING_TITLES = ["Initial Discovery Call", "Product Demo", "Technical Deep Dive", "Pricing Discussion", "Contract Negotiation"]

# Configuration for Calls
# CALL_TYPES = ["Outbound", "Inbound"]
# CALL_SUBJECTS = ["Cold Outreach", "Follow-up", "Support Inquiry", "Billing Question", "Check-in"]

# Baseline date to use (since random dates are disabled, we generate structured sequential dates)
# BASELINE_DATE = "2023-10-01 09:00:00"
START_DATE = "2024-01-01"
END_DATE = "2026-06-24"