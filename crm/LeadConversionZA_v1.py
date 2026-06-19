# Lead conversion prediction v1
# XGBoost 
# using columns lead_source, industry, no. of followups, built in score
# Works in zoho analytics code studio 

from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import joblib
import os
from pandas import DataFrame
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from sklearn.metrics import classification_report

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
        training_data_table_name = "Leads"
        columns = ["company", "followups", "industry", "isConverted", "lead_id",
                   "mobile", "name", "score", "source", "website"]
        target_column = "isConverted"
        model_name = 'lead_conversion_prediction_model'
        resultant_column_name = 'Prediction'
        non_feature_columns = ["company", "lead_id", "mobile", "name", "website"]

        data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")

        data["isConverted"] = data["isConverted"].map({
            "Yes": 1,
            "No": 0
        })
        data = data.dropna(subset=["isConverted"])
        # Fill missing categories before encoding so LabelEncoder never sees NaN
        label_encoders = {}
        for column in ["industry", "source"]:
            data[column] = data[column].fillna("Unknown").astype(str)
            le = LabelEncoder()
            data[column] = le.fit_transform(data[column])
            label_encoders[column] = le

        data.fillna(data.median(numeric_only=True), inplace=True)

        X = data.drop([target_column] + non_feature_columns, axis=1)
        y = data[target_column]

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # train XGBoost model
        model = xgb.XGBClassifier()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        output = pd.DataFrame({resultant_column_name: y_pred})
        self.log.INFO(output)

        # Evaluate the model
        print(classification_report(y_test, y_pred))

        # Save Trained Model
        directory = 'models'
        os.makedirs(directory, exist_ok=True)

        # Bundle the model together with the label encoders so that prediction
        artifact = {
            'model': model,
            'encoders': label_encoders,
            'feature_columns': list(X.columns),
        }
        model_path = os.path.join(directory, model_name + '.pkl')
        joblib.dump(artifact, model_path)

        self.ms.store_model(model_name, model_path)

        self.log.INFO("Training Completed...Proceed to Predict")

    def predict(self):
        # Path to the 'models' directory
        training_data_table_name = "Leads1"
        columns = ["company", "followups", "industry", "isConverted", "lead_id",
                   "mobile", "name", "score", "source", "website"]
        target_column = "isConverted"
        model_name = 'lead_conversion_prediction_model'
        resultant_column_name = 'Prediction'
        resultant_table_name = "lead_conversion_predictions"
        import_type = "truncateadd"
        non_feature_columns = ["company", "lead_id", "mobile", "name", "website"]

        # list models
        self.ms.list_models()

        # Load the model + the encoders that were fit during training
        model_path = self.ms.get_model_path(model_name)
        artifact = joblib.load(model_path)
        model = artifact['model']
        label_encoders = artifact['encoders']
        feature_columns = artifact['feature_columns']

        new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")

        # Keep the lead_id around for the output table before it gets dropped as a feature
        lead_ids = new_data["lead_id"]

        for column, le in label_encoders.items():
            if column in new_data.columns:
                new_data[column] = new_data[column].fillna("Unknown").astype(str)
                # Map any category never seen during training to the encoder's first class
                unseen_mask = ~new_data[column].isin(le.classes_)
                if unseen_mask.any():
                    new_data.loc[unseen_mask, column] = le.classes_[0]
                new_data[column] = le.transform(new_data[column])

        # Handle missing values the same way training did
        new_data.fillna(new_data.median(numeric_only=True), inplace=True)

        # Drop the same non-feature columns (and target) that were dropped during training,
        # so the columns fed to the model line up with what it was trained on.
        X_new = new_data.drop([target_column] + non_feature_columns, axis=1, errors="ignore")
        X_new = X_new[feature_columns]

        # Predict conversion probability using the trained model
        y_pred_new = model.predict_proba(X_new)[:, 1]

        output = pd.DataFrame({'lead_id': lead_ids, resultant_column_name: (y_pred_new * 100).round(2).astype("float64")})

        self.dt.upload_tabledata_from_DataFrame(resultant_table_name, output, {"importType": import_type})