"""
Local Configuration file for LeadConversionZA_v6.py
Runs without Zoho Analytics module - uses local CSV files instead
"""

import os

# ============================================================================
# DATA PATHS
# ============================================================================
# Base data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CRM_DIR = os.path.join(os.path.dirname(__file__), "crm")

# Input CSV files for training and prediction
TRAINING_DATA_FILE = os.path.join(DATA_DIR, "ML_Query_Table.csv")  # Must have training data
PREDICTION_DATA_FILE = os.path.join(DATA_DIR, "ML_Query_Table.csv")  # Can be same or different
OUTPUT_PREDICTIONS_FILE = os.path.join(CRM_DIR, "predictions_output.csv")

# ============================================================================
# MODEL STORAGE
# ============================================================================
MODELS_DIR = os.path.join(os.path.dirname(__file__), "crm", "models")
MODEL_NAME = "lead_conversion_pred_models"
MODEL_FILE_PATH = os.path.join(MODELS_DIR, f"{MODEL_NAME}.pkl")

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# ============================================================================
# ML MODEL CONFIGURATION
# ============================================================================

# Target and feature columns
TARGET_COLUMN = "Converted"
LEAD_ID_COLUMN = "Lead_ID"

# Columns to fetch from CSV
ML_COLUMNS = [
    "Converted",
    "Lead_Industry",
    "Lead_Source",
    "Lead_ID",
    "NumberOfCalls",
    "NumberOfMeetings",
    "NumberOfOtherTasks",
    "Member_Status",
    "Campaign_Name"
]

# Feature engineering configuration
CATEGORICAL_COLUMNS = [
    "Lead_Industry",
    "Lead_Source",
    "Member_Status",
    "Campaign_Name"
]

NUMERIC_COLUMNS = [
    "NumberOfCalls",
    "NumberOfMeetings",
    "NumberOfOtherTasks"
]

# Missing value handling
NUMERIC_IMPUTE_STRATEGY = "median"
CATEGORICAL_IMPUTE_STRATEGY = "constant"
CATEGORICAL_FILL_VALUE = "Unknown"

# ============================================================================
# HYPERPARAMETERS FOR GRID SEARCH
# ============================================================================

# Decision Tree parameters
DT_GRID_PARAMS = {
    "classifier__max_depth": [3, 5, 10, None]
}
DT_RANDOM_STATE = 42

# Random Forest parameters
RF_GRID_PARAMS = {
    "classifier__n_estimators": [100, 200]
}
RF_RANDOM_STATE = 42

# XGBoost parameters
XGB_GRID_PARAMS = {
    "classifier__max_depth": [3, 5, 6]
}
XGB_RANDOM_STATE = 42
XGB_EVAL_METRIC = "logloss"

# GridSearchCV configuration
GRID_SEARCH_CV_FOLDS = 5
GRID_SEARCH_SCORING = "accuracy"

# Train-Test Split
TEST_SIZE = 0.2
TRAIN_RANDOM_STATE = 42

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Predictions output format
OUTPUT_PREDICTIONS = True
PREDICTION_COLUMNS = [
    "Lead_ID",
    "Prediction_Decision_Tree",
    "Prediction_Random_Forest",
    "Prediction_XGBoost"
]

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join(os.path.dirname(__file__), "crm", "lead_conversion.log")

# ============================================================================
# DATABASE CONFIGURATION (Alternative to CSV if using SQLite/PostgreSQL)
# ============================================================================
# Uncomment and configure if using database instead of CSV

# DATABASE_TYPE = "sqlite"  # Options: sqlite, postgresql, mysql
# SQLITE_DB_PATH = os.path.join(DATA_DIR, "crm_data.db")
# TRAINING_DATA_QUERY = "SELECT * FROM ML_Query_Table"
# PREDICTION_DATA_QUERY = "SELECT * FROM ML_Query_Table"
# OUTPUT_TABLE_NAME = "prediction_algorithms"

# PostgreSQL/MySQL options:
# DB_HOST = "localhost"
# DB_PORT = 5432
# DB_NAME = "crm_database"
# DB_USER = "username"
# DB_PASSWORD = "password"

# ============================================================================
# FEATURE SETTINGS
# ============================================================================

# Handle unknown categories during prediction
HANDLE_UNKNOWN_CATEGORIES = "ignore"

# OneHotEncoder configuration
ONE_HOT_DROP = None  # Options: None, 'first', 'if_binary'
ONE_HOT_SPARSE_OUTPUT = False

# ============================================================================
# VALIDATION & TESTING
# ============================================================================

# Drop rows with missing target values
DROP_NA_TARGET = True

# Minimum rows required for training
MIN_TRAINING_SAMPLES = 100

# Cross-validation folds
CV_FOLDS = 5

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_config():
    """
    Validates that all required configuration values are set.
    Raises ValueError if configuration is incomplete.
    """
    required_files = {
        "TRAINING_DATA_FILE": TRAINING_DATA_FILE,
        "MODELS_DIR": MODELS_DIR,
    }
    
    for key, path in required_files.items():
        if key.endswith("_FILE") and not os.path.exists(path):
            print(f"WARNING: {key} not found at {path}")
            print("Please ensure the CSV file exists or adjust the path in config_local.py")
        elif key.endswith("_DIR") and not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")

def get_config():
    """
    Returns a dictionary of all configuration values.
    Useful for debugging and verification.
    """
    return {
        "DATA_DIR": DATA_DIR,
        "TRAINING_DATA_FILE": TRAINING_DATA_FILE,
        "PREDICTION_DATA_FILE": PREDICTION_DATA_FILE,
        "MODEL_FILE_PATH": MODEL_FILE_PATH,
        "TARGET_COLUMN": TARGET_COLUMN,
        "CATEGORICAL_COLUMNS": CATEGORICAL_COLUMNS,
        "NUMERIC_COLUMNS": NUMERIC_COLUMNS,
        "ML_COLUMNS": ML_COLUMNS
    }

# Validate on import
if __name__ != "__main__":
    validate_config()
