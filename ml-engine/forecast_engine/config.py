"""
Konfigurasi Forecast Engine (prediksi konsumsi energi).
n_estimators dijaga moderat agar training cepat di CPU biasa dengan
trade-off akurasi yang minim untuk skala data MVP.
"""
RANDOM_SEED = 42
TEST_SIZE_RATIO = 0.2

MODEL_CONFIGS = {
    "random_forest": {
        "n_estimators": 120,
        "max_depth": 10,
        "min_samples_leaf": 3,
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
    },
    "xgboost": {
        "n_estimators": 150,
        "max_depth": 5,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
    },
    "lightgbm": {
        "n_estimators": 150,
        "max_depth": -1,
        "num_leaves": 31,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
        "verbose": -1,
    },
}
