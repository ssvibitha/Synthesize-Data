from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import joblib
import os
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, f1_score
from sklearn.model_selection import GridSearchCV
import shap
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
        training_data_table_name = "AccountHistorical.csv"
        model_name = 'account_health_score'
        target_column = "Churn"
        non_feature_columns = ["Account Id"]
        feature_columns = ["InvoiceAmount","OpenCasesPercent","OverduePercent","Invoice Count",
        "NumCaseEscalation","EscalationRate","AvgResolutionTime"]

        data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, [], "")
        
        data = data.dropna(subset=[target_column])
        X = data[feature_columns].copy()
        
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        X= pd.DataFrame(X,columns=feature_columns)
            
        y = data[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        logR_param_grid = {
            'penalty': ['l1', 'l2'],
            'C': [0.01, 0.1, 1, 10, 100],
            'solver': ['liblinear', 'saga']
        }
        logR_grid = GridSearchCV(
            LogisticRegression(random_state=42, max_iter=1000),
            logR_param_grid,
            cv=5,
            scoring='roc_auc',
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
            scoring='roc_auc',
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
            scoring='roc_auc',
            n_jobs=-1,
            return_train_score=True
        )
        models = {
            'Logistic Regression': logR_grid,
            'Random Forest': rf_grid,
            'XGBoost': xgb_grid
        }
        best_overall_model = None
        best_overall_score = -1
        best_overall_name = ""
        for name, model in models.items():
            model.fit(X_train, y_train)
            self.log.INFO(f"{name} Best Params: {model.best_params_}")
            
            best_model = model.best_estimator_
            y_pred = best_model.predict(X_test)
            
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
            
            if roc > best_overall_score:
                best_overall_score = roc
                best_overall_model = best_model
                best_overall_name = name
                best_overall_importances = importances
        self.log.INFO(f"Selected Best Model: {best_overall_name} with ROC-AUC score {best_overall_score:.4f}")
        
        directory = 'models'
        os.makedirs(directory, exist_ok=True) 
        artifact = {
            'model': best_overall_model,
            'model_name': best_overall_name,
            'feature_columns': feature_columns,
            'feature_importances': best_overall_importances,
        }
        model_path = os.path.join(directory, model_name + '.pkl')
        joblib.dump(artifact, model_path)
        self.ms.store_model(model_name, model_path)
        self.log.INFO("Training Completed")

    def predict(self):
        training_data_table_name = "AccountQueryTable.csv"
        model_name = 'account_health_score'
        resultant_table_name = "AccountScores.csv"
        id_col = "Account Id"

        import_type = "truncateadd"

        self.ms.list_models()
        model_path = self.ms.get_model_path(model_name)
        artifact = joblib.load(model_path)
        model = artifact['model']
        feature_columns = artifact['feature_columns']
        feature_importances = artifact['feature_importances']
        new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, [], "")
        acc_ids = new_data[id_col]
        new_data.fillna(new_data.median(numeric_only=True), inplace=True)

        scaler = MinMaxScaler()

        X_new = pd.DataFrame()

        for col in feature_columns:
            if col in new_data.columns:
                X_new[col] = new_data[col]
            else:
                X_new[col] = 0

        X_new = scaler.fit_transform(X_new)
        X_new= pd.DataFrame(X_new,columns=feature_columns)

        output = pd.DataFrame({'Account Id': acc_ids})
        proba_churn = model.predict_proba(X_new)[:, 1]
        output["score"] = np.round(100 * (1 - proba_churn), 2)
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_new)

        self.dt.upload_tabledata_from_DataFrame(resultant_table_name, output, {"importType": import_type})
        self.log.INFO("Prediction Completed")