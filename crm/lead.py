import pandas as pd
from xgboost import XGBClassifier
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class LocalLogger:
    def INFO(self, msg):
        print(f"[INFO] {msg}")
    def ERROR(self, msg):
        print(f"[ERROR] {msg}")

class MLModel:
    def __init__(self):
        self.log = LocalLogger()
        # Paths relative to the script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.script_dir, "leads (1).csv")
        self.model_dir = os.path.join(self.script_dir, "models")
        self.model_path = os.path.join(self.model_dir, "lead_model.pkl")
        self.predictions_path = os.path.join(self.script_dir, "lead_predictions.csv")

    def fit(self):
        try:
            self.log.INFO("In fit function")
            print("Entered fit function")
        
            # Load from local CSV instead of Zoho Analytics
            self.log.INFO(f"Reading lead data from: {self.csv_path}")
            lead_data = pd.read_csv(self.csv_path)

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
            os.makedirs(self.model_dir, exist_ok=True)

            joblib.dump(model, self.model_path)
            self.log.INFO(f"Saved model locally to: {self.model_path}")
            self.log.INFO("Training Completed")

        except Exception as e:
            self.log.ERROR("TRAINING FAILED: " + str(e))
            print("FULL ERROR:", str(e))
            raise e

    def predict(self):
        try:
            self.log.INFO(f"Loading model from: {self.model_path}")
            model = joblib.load(self.model_path)
            
            # Load from local CSV instead of Zoho Analytics
            self.log.INFO(f"Reading new data for prediction from: {self.csv_path}")
            new_data = pd.read_csv(self.csv_path)

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

            # Save locally instead of uploading to Zoho Analytics
            output.to_csv(self.predictions_path, index=False)
            self.log.INFO(f"Saved predictions locally to: {self.predictions_path}")

            self.log.INFO("Prediction Completed")
            print("Prediction Completed Successfully")
        except Exception as e:
            self.log.ERROR("PREDICTION FAILED: " + str(e))
            print("PREDICTION ERROR:", str(e))
            raise e

if __name__ == "__main__":
    ml_pipeline = MLModel()
    
    print("Starting ML pipeline execution")
    ml_pipeline.fit()
    print("\n--- Training finished. Starting predictions ---")
    ml_pipeline.predict()