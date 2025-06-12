import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix
)
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load preprocessed data
df = pd.read_csv("processed_commands.csv")

# 2. Prepare command labels
df["command"] = df["command_bit1"] * 2 + df["command_bit0"]

# 3. Stratified train-validation split on index for sequence construction
indices = df.index.values
commands = df["command"].values
train_idx, val_idx, y_train_cmd, y_val_cmd = train_test_split(
    indices, commands, test_size=0.2, random_state=42, stratify=commands
)

# 4. Sequence creation function
# Adjust to include relevant features

def create_sequences(df, idxs, seq_len, feature_cols=None, model_type='LSTM'):
    if feature_cols is None:
        # Adjust features based on model type
        if model_type == 'LSTM':
            # LSTM expects 2 features
            feature_cols = ["command_bit1", "command_bit0"]
        elif model_type == 'CNN':
            # CNN might expect different features
            feature_cols = ["command_bit1", "command_bit0", "param_bit5", "param_bit4", "param_bit3", "param_bit2", "param_bit1", "param_bit0"]
        else:
            # Default for Transformer
            feature_cols = ["command_bit1", "command_bit0"]
    
    X, y = [], []
    for idx in idxs:
        if idx + seq_len < len(df):
            seq = df.iloc[idx:idx+seq_len][feature_cols].values
            target = df.iloc[idx + seq_len]["command"]
            X.append(seq)
            y.append(target)
    return np.array(X), np.array(y)

# Create sequences for each model
X_lstm_val, y_lstm_val = create_sequences(df, val_idx, seq_len=5, model_type='LSTM')
X_trans_val, y_trans_val = create_sequences(df, val_idx, seq_len=5, model_type='Transformer')
X_cnn_val, y_cnn_val   = create_sequences(df, val_idx, seq_len=12, model_type='CNN')

# Print shapes for debugging
print(f"Data shapes:")
print(f"LSTM: X={X_lstm_val.shape}, y={y_lstm_val.shape}")
print(f"Transformer: X={X_trans_val.shape}, y={y_trans_val.shape}")
print(f"CNN: X={X_cnn_val.shape}, y={y_cnn_val.shape}")
print(f"Unique classes: {np.unique(commands)}")
print()

# 5. Load trained models
# If your models are TensorFlow Keras .h5 files:
import tensorflow as tf
from tensorflow.keras import losses, metrics

# Define custom objects dictionary to handle legacy metric names
custom_objects = {
    'mse': losses.MeanSquaredError(),
    'mae': losses.MeanAbsoluteError(),
    'accuracy': metrics.Accuracy(),
    'sparse_categorical_crossentropy': losses.SparseCategoricalCrossentropy(),
    'categorical_crossentropy': losses.CategoricalCrossentropy()
}

# Try loading models with error handling
models = {}

try:
    print("Loading LSTM model...")
    models['LSTM'] = tf.keras.models.load_model("LSTM.h5", custom_objects=custom_objects)
    print("LSTM model loaded successfully.")
except Exception as e:
    print(f"Error loading LSTM model: {e}")
    models['LSTM'] = None

try:
    print("Loading Transformer model...")
    models['Transformer'] = tf.keras.models.load_model("Transformer.h5", custom_objects=custom_objects, compile=False)
    print("Transformer model loaded successfully.")
except Exception as e:
    print(f"Error loading Transformer model: {e}")
    models['Transformer'] = None

try:
    print("Loading CNN model...")
    models['CNN'] = tf.keras.models.load_model("cnn-model.keras", custom_objects=custom_objects)
    print("CNN model loaded successfully.")
except Exception as e:
    print(f"Error loading CNN model: {e}")
    models['CNN'] = None

# Filter out models that failed to load
loaded_models = {name: model for name, model in models.items() if model is not None}
print(f"\nSuccessfully loaded models: {list(loaded_models.keys())}")

# 6. Get predictions from loaded models
predictions = {}
classes = np.unique(commands)

if 'LSTM' in loaded_models:
    print("Getting LSTM predictions...")
    lstm_output = loaded_models['LSTM'].predict(X_lstm_val)
    # Handle tuple output from model
    if isinstance(lstm_output, (list, tuple)):
        lstm_probs = lstm_output[0] if len(lstm_output) > 0 else lstm_output
    else:
        lstm_probs = lstm_output
    y_lstm_pred = np.argmax(lstm_probs, axis=1)
    y_lstm_bin = label_binarize(y_lstm_val, classes=classes)
    predictions['LSTM'] = (y_lstm_val, y_lstm_pred, y_lstm_bin, lstm_probs)

if 'Transformer' in loaded_models:
    print("Getting Transformer predictions...")
    trans_probs = loaded_models['Transformer'].predict(X_trans_val)
    y_trans_pred = np.argmax(trans_probs, axis=1)
    y_trans_bin = label_binarize(y_trans_val, classes=classes)
    predictions['Transformer'] = (y_trans_val, y_trans_pred, y_trans_bin, trans_probs)

if 'CNN' in loaded_models:
    print("Getting CNN predictions...")
    cnn_probs = loaded_models['CNN'].predict(X_cnn_val)
    y_cnn_pred = np.argmax(cnn_probs, axis=1)
    y_cnn_bin = label_binarize(y_cnn_val, classes=classes)
    predictions['CNN'] = (y_cnn_val, y_cnn_pred, y_cnn_bin, cnn_probs)

# 7. Compute metrics
def compute_metrics(y_true, y_pred, y_bin, probs):
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted"
    )
    roc = roc_auc_score(y_bin, probs, average="macro", multi_class="ovr")
    cm = confusion_matrix(y_true, y_pred)
    return acc, prec, rec, f1, roc, cm

metrics = {}
for name, (y_val, y_pred, y_bin, probs) in predictions.items():
    metrics[name] = compute_metrics(y_val, y_pred, y_bin, probs)

# 10. Display summary table
results = pd.DataFrame({
    name: {
        "Accuracy": m[0],
        "Precision": m[1],
        "Recall": m[2],
        "F1 Score": m[3],
        "ROC-AUC": m[4]
    }
    for name, m in metrics.items()
}).T
print("Summary of Command Classification Metrics:")
print(results)

# 11. Plot confusion matrices
for name, m in metrics.items():
    cm = m[5]
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"{name} Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.show()
