# Lead conversion prediction v2
# Random Forest, Decision tree, XGBoost
# Using columns no. of meetings,calls,tasks, lead_source, industry
# Works in zoho analytics code studio 

from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import joblib
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

class MLModel:
    dt: DataTransformationUtil = None
    za: ZohoAnalytics = None
    ms: ModelStorage = None

    def __init__(self, za, ms):
        self.za = za
        self.dt = DataTransformationUtil(self.za)
        self.log = self.za.context.log
        self.ms = ms

    def fit(self):
        training_data_table_name = "ML_Query_Table"
        columns = ["Converted", "l.Industry", "l.Lead Source", "Lead_ID", "NumberOfCalls", "NumberOfMeetings", "NumberOfTasks"]
        target_column = "Converted"
        model_name = 'lead_conversion_pred_models'
        non_feature_columns = ["Lead_ID"]

        data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")
        
        data = data.dropna(subset=["Converted"])
        
        # Fill missing categories before encoding
        label_encoders = {}
        for column in ["l.Industry", "l.Lead Source"]:
            data[column] = data[column].fillna("Unknown").astype(str)
            le = LabelEncoder()
            data[column] = le.fit_transform(data[column])
            label_encoders[column] = le

        data.fillna(data.median(numeric_only=True), inplace=True)

        X = data.drop([target_column] + non_feature_columns, axis=1)
        y = data[target_column]

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        models = {
            'Decision Tree': DecisionTreeClassifier(random_state=42),
            'Random Forest': RandomForestClassifier(random_state=42),
            'XGBoost': xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
        }

        trained_models = {}

        for name, model in models.items():
            model.fit(X_train, y_train)
            trained_models[name] = model
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            self.log.INFO(f"--- {name} Results ---")
            
            # 1. Model Accuracy
            acc = accuracy_score(y_test, y_pred)
            self.log.INFO(f"Accuracy: {acc:.4f}")
            
            # 2. Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            self.log.INFO(f"Confusion Matrix:\n{cm}")
            
            # 3. Feature Importance
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_imp_df = pd.DataFrame({
                    'Feature': X.columns, 
                    'Importance': importances
                }).sort_values(by='Importance', ascending=False)
                self.log.INFO(f"Feature Importances:\n{feature_imp_df.to_string(index=False)}")
                
            self.log.INFO("-" * 30)

        # Save Trained Model
        directory = 'models'
        os.makedirs(directory, exist_ok=True)

        artifact = {
            'models': trained_models,
            'encoders': label_encoders,
            'feature_columns': list(X.columns),
        }
        model_path = os.path.join(directory, model_name + '.pkl')
        joblib.dump(artifact, model_path)

        self.ms.store_model(model_name, model_path)

        self.log.INFO("Training Completed...Proceed to Predict")

    def predict(self):
        training_data_table_name = "ML_Query_Table"
        columns = ["Converted", "l.Industry", "l.Lead Source", "Lead_ID", "NumberOfCalls", "NumberOfMeetings", "NumberOfTasks"]
        target_column = "Converted"
        model_name = 'lead_conversion_pred_models'
        resultant_table_name = "lead_conversion_predictions"
        import_type = "truncateadd"
        non_feature_columns = ["Lead_ID"]

        self.ms.list_models()

        model_path = self.ms.get_model_path(model_name)
        artifact = joblib.load(model_path)
        models = artifact['models']
        label_encoders = artifact['encoders']
        feature_columns = artifact['feature_columns']

        new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")

        lead_ids = new_data["Lead_ID"]

        for column, le in label_encoders.items():
            if column in new_data.columns:
                new_data[column] = new_data[column].fillna("Unknown").astype(str)
                # Map unseen classes
                unseen_mask = ~new_data[column].isin(le.classes_)
                if unseen_mask.any():
                    new_data.loc[unseen_mask, column] = le.classes_[0]
                new_data[column] = le.transform(new_data[column])

        new_data.fillna(new_data.median(numeric_only=True), inplace=True)

        X_new = new_data.drop([target_column] + non_feature_columns, axis=1, errors="ignore")
        X_new = X_new[feature_columns]

        # Predict conversion probability using the trained models
        output = pd.DataFrame({'Lead_ID': lead_ids})
        
        for name, model in models.items():
            col_name = f'Prediction_{name.replace(" ", "_")}'
            output[col_name] = (model.predict_proba(X_new)[:, 1] * 100).round(2).astype("float64")

        self.dt.upload_tabledata_from_DataFrame(resultant_table_name, output, {"importType": import_type})