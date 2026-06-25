# Lead conversion prediction v5
# For 10000 leads
# Random Forest, Decision tree, XGBoost
# Using columns-no. of meetings,calls,other tasks, lead_source, industry, campaigns
# Other tasks = NumberOfTasks - NumberOfMeeting - NumberOfCalls
# Works in zoho analytics code studio 
# Use gridsearch for finetuning

from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import joblib
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, f1_score
from sklearn.model_selection import GridSearchCV

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
        columns = ["Converted","Lead_Industry" , "Lead_Source", "Lead_ID", "NumberOfCalls", 
            "NumberOfMeetings", "NumberOfOtherTasks", "Member_Status", "Campaign_Name"]
        target_column = "Converted"
        model_name = 'lead_conversion_pred_models'
        non_feature_columns = ["Lead_ID"]
        
        categorical_col=["Lead_Industry", "Lead_Source", "Member_Status", "Campaign_Name"]
        
        data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")
        
        data = data.dropna(subset=["Converted"])
        for col in ["NumberOfCalls","NumberOfMeetings","NumberOfOtherTasks"]:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        # Fill missing categories before encoding
        label_encoders = {}
        for column in categorical_col:
            data[column] = data[column].fillna("Unknown").astype(str)
            le = LabelEncoder()
            data[column] = le.fit_transform(data[column])
            label_encoders[column] = le

        data.fillna(data.median(numeric_only=True), inplace=True)

        X = data.drop([target_column] + non_feature_columns, axis=1)
        y = data[target_column]

        # Split data into training and testing sets, stratify=y to preserve data distribution
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        dt_param_grid = {
            'criterion': ['gini', 'entropy'],
            'max_depth': [3, 5, 10, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        dt_grid = GridSearchCV(
            DecisionTreeClassifier(random_state=42),
            dt_param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            return_train_score=True
        )
        rf_param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        rf_grid = GridSearchCV(
            RandomForestClassifier(random_state=42),
            rf_param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            return_train_score=True
        )
        xgb_param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 6],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0]
        }
        xgb_grid = GridSearchCV(
            XGBClassifier(
                random_state=42,
                eval_metric='logloss'
            ),
            xgb_param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            return_train_score=True
        )
        models = {
            'Decision Tree': dt_grid,
            'Random Forest': rf_grid,
            'XGBoost': xgb_grid
        }

        trained_models = {}

        for name, model in models.items():
            model.fit(X_train, y_train)
            self.log.INFO(f"Best Params: {model.best_params_}")
            self.log.INFO(f"Best CV Score: {model.best_score_:.4f}")
            best_model = model.best_estimator_
            trained_models[name] = best_model

            # Make predictions
            y_pred = best_model.predict(X_test)
            
            self.log.INFO(f"{name} Results")
            
            # 1. Model Accuracy
            acc = accuracy_score(y_test, y_pred)
            self.log.INFO(f"Accuracy: {acc:.4f}")
            
            # 2. Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            self.log.INFO(f"Confusion Matrix:\n{cm}")

            # 3. ROC-AUC Score in case the model predicts either 0 or 1
            y_prob = best_model.predict_proba(X_test)[:, 1]
            try:
                roc = roc_auc_score(y_test, y_prob)
                self.log.INFO(f"ROC-AUC score: {roc:.4f}")
            except:
                self.log.INFO("ROC-AUC could not be computed")

            # 4. f1 Score
            f1 = f1_score(y_test, y_pred)
            self.log.INFO(f"f1 Score: {f1:.4f}")
            
            # 5. Feature Importance
            if hasattr(best_model, 'feature_importances_'):
                importances = best_model.feature_importances_
                feature_imp_df = pd.DataFrame({
                    'Feature': X.columns, 
                    'Importance': importances*100
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

        self.log.INFO("Training Completed")

    def predict(self):
        training_data_table_name = "ML_Query_Table"
        columns = ["Converted", "Lead_Industry", "Lead_Source", "Lead_ID", "NumberOfCalls", "NumberOfMeetings", 
        "NumberOfOtherTasks", "Member_Status", "Campaign_Name"]
        target_column = "Converted"
        model_name = 'lead_conversion_pred_models'
        resultant_table_name = "prediction_algorithms"
        import_type = "truncateadd"
        non_feature_columns = ["Lead_ID"]

        self.ms.list_models()

        model_path = self.ms.get_model_path(model_name)
        artifact = joblib.load(model_path)
        models = artifact['models']
        label_encoders = artifact['encoders']
        feature_columns = artifact['feature_columns']

        new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, columns, "")
        for col in ["NumberOfCalls","NumberOfMeetings","NumberOfOtherTasks"]:
            new_data[col] = pd.to_numeric(new_data[col], errors="coerce")
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