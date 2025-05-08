import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
import pickle
import os

# === Model Definition ===
class MultiTaskContrastiveModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(MultiTaskContrastiveModel, self).__init__()
        self.shared_layer1 = nn.Linear(input_dim, hidden_dim)
        self.shared_layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.shared_layer3 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.batch_norm1 = nn.BatchNorm1d(hidden_dim)
        self.batch_norm2 = nn.BatchNorm1d(hidden_dim)
        self.dropout = nn.Dropout(p=0.3)
        self.classifier = nn.Linear(hidden_dim // 2, output_dim)
        self.p7_p11_classifier = nn.Linear(hidden_dim // 2, 2)
        self.embedding_layer = nn.Linear(hidden_dim // 2, 32)

    def forward(self, x):
        shared = torch.relu(self.batch_norm1(self.shared_layer1(x)))
        shared = self.dropout(shared)
        shared = torch.relu(self.batch_norm2(self.shared_layer2(shared)))
        shared = torch.relu(self.shared_layer3(shared))
        class_out = self.classifier(shared)
        p7_p11_out = self.p7_p11_classifier(shared)
        embedding = self.embedding_layer(shared)
        return class_out, p7_p11_out, embedding

# === Model Initialization and Loading ===
input_dim = 13  # 13 selected features embedded directly
hidden_dim = 128
output_dim = 6

model_path = "/path/to/passage_prediction_model.pth"
model = MultiTaskContrastiveModel(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# === Prediction Function ===
def preprocess_and_predict(input_file, output_file):
    with open("/path/to/clustering_params.pkl", "rb") as f:
        clustering_objects = pickle.load(f)
    scaler = clustering_objects["scaler"]
    pca = clustering_objects["pca"]
    kmeans = clustering_objects["kmeans"]
    dbscan = clustering_objects["dbscan"]
    cluster_to_label_prob = clustering_objects["cluster_to_label_prob"]
    
    # Load data
    df = pd.read_excel(input_file, usecols=[4, 13, 14]).dropna().values
    kde = gaussian_kde(df.T)
    density = kde(df.T)

    center = df[np.argmax(density)]
    distances_from_center = np.linalg.norm(df - center, axis=1)
    spread_array = np.full(df.shape[0], distances_from_center.mean())
    density_gradient = np.gradient(density)
    local_mean_density = np.array([
        density[np.linalg.norm(df - point, axis=1) < distances_from_center.mean()].mean()
        for point in df
    ])
    outlier_score = 1 / (density + 1e-6)
    log_distances = np.log1p(distances_from_center)
    distance_variance = np.full(df.shape[0], np.var(distances_from_center))

    # Clustering
    clustering_data = scaler.transform(df[:, :3])
    clustering_data = pca.transform(clustering_data)
    kmeans_labels = kmeans.predict(clustering_data)
    dbscan_labels = dbscan.fit_predict(clustering_data)

    prob_features = cluster_to_label_prob[kmeans_labels]
    dbscan_p15_feature = (dbscan_labels == 5).astype(int).reshape(-1, 1)
    kmeans_labels_reshaped = kmeans_labels.reshape(-1, 1)

    # Compose final input features (manually selected)
    final_features = np.column_stack((
        spread_array.reshape(-1, 1),          # Spread (Feature 5)
        local_mean_density.reshape(-1, 1),    # Local Mean Density (Feature 10)
        distance_variance.reshape(-1, 1),     # Distance Variance (Feature 16)
        outlier_score.reshape(-1, 1),         # Outlier Score (Feature 11)
        log_distances.reshape(-1, 1),         # Log Distance (Feature 15)
        dbscan_p15_feature,                   # DBSCAN Feature (Feature 17)
        prob_features,                        # Cluster Probabilities (Features 18–23)
        kmeans_labels_reshaped               # KMeans Label (Feature 24)
    ))

    # Predict
    new_data_tensor = torch.tensor(final_features, dtype=torch.float32)
    with torch.no_grad():
        class_out, _, _ = model(new_data_tensor)
        probabilities = torch.softmax(class_out, dim=1).numpy()

    # Save prediction results
    class_columns = ['P5_Prob', 'P7_Prob', 'P9_Prob', 'P11_Prob', 'P13_Prob', 'P15_Prob']
    result_df = pd.DataFrame({
        "Cell Size": df[:, 0],
        "ROS Efflux": df[:, 1],
        "RI": df[:, 2],
        **{class_columns[i]: probabilities[:, i] for i in range(len(class_columns))}
    })
    result_df.to_excel(output_file, index=False)
    print(f"Prediction results saved to {output_file}")

# === Run Prediction ===
input_file = "/path/to/your_input_file.xlsx"
output_file = "/path/to/prediction_result.xlsx"
preprocess_and_predict(input_file, output_file)
