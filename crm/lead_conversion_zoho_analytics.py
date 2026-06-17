from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import pandas as pd
from xgboost import XGBClassifier
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
        try:
            self.log.INFO("In fit function")
            print("Entered fit function")
        
            lead_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(
                "leads1", 
                ["company", "followups", "industry", "isConverted", "lead_id", "mobile", "name", "score", "source", "website"],
                ""
            )

            X = lead_data[["source", "industry", "score", "followups"]]

            X["score"] = pd.to_numeric(X["score"], errors="coerce")
            X["followups"] = pd.to_numeric(X["followups"], errors="coerce")
            X = X.fillna(0)

            y = lead_data["isConverted"].astype(str).str.strip().str.lower().map({
                "yes": 1,
                "no": 0
            })

            X = pd.get_dummies(X, columns=["source", "industry"])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
            model.fit(X_train, y_train)

            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)

            self.log.INFO("Accuracy = " + str(acc))
            os.makedirs("models", exist_ok=True)

            model_path = "models/lead_model.pkl"
            joblib.dump(model, model_path)

            self.ms.store_model("lead_model", model_path)
            self.log.INFO("Training Completed")

        except Exception as e:
            self.log.ERROR("TRAINING FAILED: " + str(e))
            print("FULL ERROR:", str(e))
            raise e

    def predict(self):
        try:
            model_path = self.ms.get_model_path("lead_model")
            model = joblib.load(model_path)
            new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(
                "Leads",
                ["lead_id", "source", "industry", "score", "followups"],
                ""
            )

            X_new = new_data[["source", "industry", "score", "followups"]]
            X_new = pd.get_dummies(X_new, columns=["source", "industry"])
            X_train_cols = model.get_booster().feature_names
            X_new = X_new.reindex(columns=X_train_cols, fill_value=0)

            pred_class = model.predict(X_new)
            pred_prob = model.predict_proba(X_new)[:, 1]

            output = pd.DataFrame({
                "lead_id": new_data["lead_id"],
                "isConverted_Predicted": pred_class,
                "Conversion_Probability_%": pred_prob * 100
            })

            self.dt.upload_tabledata_from_DataFrame(
                "Lead_Predictions",
                output,
                {"importType": "truncateadd"}
            )

            self.log.INFO("Prediction Completed")
            print("Prediction Completed Successfully")
        except Exception as e:
            self.log.ERROR("PREDICTION FAILED: " + str(e))
            print("PREDICTION ERROR:", str(e))
            raise e
if __name__ == "__main__":
    ml_pipeline = MLModel(za, ms)
    
    print("Starting ML pipeline execution")
    ml_pipeline.fit()