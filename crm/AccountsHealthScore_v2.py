# Without Using Historical dataset
# Kmeans

import importlib
from DataTransformationUtil import DataTransformationUtil
from ZohoAnalytics import ZohoAnalytics
from ModelStorage import ModelStorage
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

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
        training_data_table_name = "AccountQueryTable.csv"
        model_name = 'account_health_score'
        non_feature_columns = ["Account Id"]
        feature_columns = ["InvoiceAmount","OpenCasesPercent","OverduePercent","Invoice Count",
        "NumCaseEscalation","EscalationRate","AvgResolutionTime"]
        data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, [], "")
        pca_weights={
            "InvoiceAmount":1,
            "OpenCasesPercent":2,
            "OverduePercent":2,
            "Invoice Count":1,
            "NumCaseEscalation":2,
            "EscalationRate":2,
            "AvgResolutionTime":2
        }
        X = data[feature_columns].copy()
        X = X.fillna(X.median(numeric_only=True))

        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        X = pd.DataFrame(X,columns=feature_columns)

        for col, weight in pca_weights.items():
            X[col] = X[col] * weight    
        pca = PCA()
        pca.fit(X)

        loadings= np.abs(pca.components_)
        importance = np.dot(pca.explained_variance_ratio_ , loadings )
        importance = importance / importance.sum() *100

        directory = 'models'
        os.makedirs(directory, exist_ok=True)
        importance_df = pd.DataFrame({
            "Feature": feature_columns,
            "Importance": importance
        })
        artifact = {
            'scaler':scaler,
            'feature_columns': feature_columns,
            'importance':importance_df
        }
        model_path = os.path.join(directory, model_name + '.pkl')
        self.dt.upload_tabledata_from_DataFrame("PCAFeatureImportance", importance_df, {"importType": "truncateadd"})
        joblib.dump(artifact, model_path)
        self.ms.store_model(model_name, model_path)
        self.log.INFO("Training Completed")

    def predict(self):
        training_data_table_name = "AccountQueryTable.csv"
        model_name = 'account_health_score'
        resultant_table_name = "PCAaccountScores"
        id_col = "Account Id"
        negative_features = ["OpenCasesPercent","OverduePercent","NumCaseEscalation","EscalationRate","AvgResolutionTime"]
        import_type = "truncateadd"

        self.ms.list_models()
        model_path = self.ms.get_model_path(model_name)
        artifact = joblib.load(model_path)
        feature_columns = artifact['feature_columns']
        scaler = artifact['scaler']
        importance_df = artifact['importance']
        new_data: pd.DataFrame = self.dt.fetch_tabledata_as_DataFrame(training_data_table_name, [], "")
        acc_ids= new_data[id_col]
        new_data.fillna(new_data.median(numeric_only=True), inplace=True)
        X_new = pd.DataFrame()

        for col in feature_columns:
            if col in new_data.columns:
                X_new[col] = new_data[col]
            else:
                X_new[col] = 0

        X_new = scaler.transform(X_new)
        X_new= pd.DataFrame(X_new,columns=feature_columns)
        
        for col in negative_features:
            X_new[col] = 1 - X_new[col]
        output = pd.DataFrame({'Account Id': acc_ids})
        output['Score'] = np.dot(X_new,importance_df['Importance'])
        self.dt.upload_tabledata_from_DataFrame(resultant_table_name, output, {"importType": import_type})
        self.log.INFO("Prediction Completed")