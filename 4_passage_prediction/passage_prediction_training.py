import pandas as pd
import re
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from tqdm import tqdm
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import gaussian_kde
from sklearn.metrics import accuracy_score, classification_report
from collections import Counter
import pickle

# === Model Definition ===
class MultiTaskContrastiveModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(MultiTaskContrastiveModel, self).__init__()
        self.shared_layer1 = nn.Linear(input_dim, hidden_dim)
        self.shared_layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.shared_layer3 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.batch_norm1 = nn.BatchNorm1d(hidden_dim)
        self.batch_norm2 = nn.BatchNorm1d(hidden_dim)
        self.dropout = nn.Dropout(p=0.5)
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

# === Dataset Class ===
class PNumberDataset(Dataset):
    def __init__(self, file_paths, clustering_base_features, selected_features, apply_clustering=True, n_clusters=6, eps=1.5, min_samples=5):
        self.selected_features = selected_features
        self.data = []
        self.labels = []
        self.label_mapping = {"P5": 0, "P7": 1, "P9": 2, "P11": 3, "P13": 4, "P15": 5}

        all_features = []
        all_labels = []

        for file_path in tqdm(file_paths, desc="Loading Data"):
            label_key = re.search(r'(P\d+)', file_path.upper()).group(1)
            label = self.label_mapping[label_key]

            df = pd.read_excel(file_path, usecols=[4, 13, 14]).dropna().values
            kde = gaussian_kde(df.T)
            density = kde(df.T)

            center = df[np.argmax(density)]
            distances_from_center = np.linalg.norm(df - center, axis=1)
            spread_array = np.full(df.shape[0], distances_from_center.mean())
            normalized_distances = distances_from_center / (distances_from_center.max() + 1e-6)
            density_gradient = np.gradient(density)
            local_mean_density = np.array([
                density[np.linalg.norm(df - point, axis=1) < distances_from_center.mean()].mean()
                for point in df
            ])
            outlier_score = 1 / (density + 1e-6)
            distance_density = distances_from_center * density
            normalized_distance_density = normalized_distances * density
            weighted_distance = distances_from_center * density

            distance_density_ratio = distances_from_center / (density + 1e-6)
            kde_local_density_product = density * local_mean_density
            spread_density_gradient = spread_array * density_gradient
            log_distances = np.log1p(distances_from_center)
            distance_variance = np.full(df.shape[0], np.var(distances_from_center))

            features = np.column_stack((
                df[:, 0],
                df[:, 1],
                df[:, 2],
                density,
                distances_from_center,
                spread_array,
                distance_density,
                normalized_distance_density,
                weighted_distance,
                density_gradient,
                local_mean_density,
                outlier_score,
                distance_density_ratio,
                kde_local_density_product,
                spread_density_gradient,
                log_distances,
                distance_variance
            ))

            all_features.append(features)
            all_labels.extend([label] * len(features))

        combined_features = np.vstack(all_features)
        combined_labels = np.array(all_labels)

        if apply_clustering:
            clustering_data = combined_features[:, clustering_base_features]

            scaler = StandardScaler()
            clustering_data = scaler.fit_transform(clustering_data)

            pca = PCA(n_components=2)
            clustering_data = pca.fit_transform(clustering_data)

            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            dbscan_labels = dbscan.fit_predict(clustering_data)

            p15_mask = (combined_labels == self.label_mapping["P15"]) & (dbscan_labels != -1)
            non_p15_mask = ~p15_mask

            p15_data = clustering_data[p15_mask]
            non_p15_data = clustering_data[non_p15_mask]
            non_p15_labels = combined_labels[non_p15_mask]

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans_labels = kmeans.fit_predict(non_p15_data)

            cluster_to_label_prob = np.zeros((n_clusters, len(self.label_mapping)))
            for cluster_id in range(n_clusters):
                cluster_labels = non_p15_labels[kmeans_labels == cluster_id]
                cluster_count = np.bincount(cluster_labels, minlength=len(self.label_mapping))
                cluster_to_label_prob[cluster_id] = cluster_count / cluster_count.sum()

            clustering_objects = {
                "scaler": scaler,
                "pca": pca,
                "kmeans": kmeans,
                "dbscan": dbscan,
                "cluster_to_label_prob": cluster_to_label_prob
            }

            with open("clustering_objects.pkl", "wb") as f:
                pickle.dump(clustering_objects, f)

            cluster_label_max = np.argmax(cluster_to_label_prob, axis=1)

            dbscan_p15_feature = (dbscan_labels == 5).astype(int)
            prob_features = cluster_to_label_prob[kmeans_labels]
            cluster_max_labels = cluster_label_max[kmeans_labels]

            full_prob_features = np.zeros((len(combined_features), len(self.label_mapping)))
            full_cluster_max_labels = np.full(len(combined_features), -1)

            full_prob_features[non_p15_mask] = prob_features
            full_cluster_max_labels[non_p15_mask] = cluster_max_labels

            combined_features = np.column_stack((combined_features, dbscan_p15_feature, full_prob_features, full_cluster_max_labels))

        self.data = torch.tensor(combined_features, dtype=torch.float32)
        self.labels = torch.tensor(combined_labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        selected_data = self.data[idx, self.selected_features]
        return selected_data, self.labels[idx]

# === File Paths ===
file_paths = [
    r"/path/to/hDF_P5.xlsx",
    r"/path/to/hDF_P7.xlsx",
    r"/path/to/hDF_P9.xlsx",
    r"/path/to/hDF_P11.xlsx",
    r"/path/to/hDF_P13.xlsx",
    r"/path/to/hDF_P15.xlsx"
]

clustering_base_features = [0, 1, 2, 4, 12]
selected_features = [5, 10, 16, 11, 15, 17, 18, 19, 20, 21, 22, 23, 24]

dataset = PNumberDataset(
    file_paths=file_paths,
    clustering_base_features=clustering_base_features,
    selected_features=selected_features,
    apply_clustering=True,
    n_clusters=6,
    eps=1.5,
    min_samples=5
)
