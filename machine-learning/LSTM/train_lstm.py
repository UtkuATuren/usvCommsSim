import pandas as pd
import numpy as np
from numpy.linalg import norm
from numpy import dot
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.metrics import SparseCategoricalAccuracy

from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_fscore_support, accuracy_score
)
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns

# ── 1. Load & preprocess ──
df = pd.read_csv("processed_commands.csv")
df["command"] = df["command_bit1"] * 2 + df["command_bit0"]
df["param"] = (
    df["param_bit5"] * 32 +
    df["param_bit4"] * 16 +
    df["param_bit3"] * 8 +
    df["param_bit2"] * 4 +
    df["param_bit1"] * 2 +
    df["param_bit0"]
)
df = df[["command", "param"]]

# ── 2. Create sequences ──
SEQ_LEN = 5
def create_sequences(df, seq_len=SEQ_LEN):
    X, y_cmd, y_param = [], [], []
    for i in range(len(df) - seq_len):
        seq = df.iloc[i:i+seq_len][["command", "param"]].values
        target_cmd = df.iloc[i+seq_len]["command"]
        target_param = df.iloc[i+seq_len]["param"]
        X.append(seq)
        y_cmd.append(target_cmd)
        y_param.append(target_param)
    return np.array(X), np.array(y_cmd), np.array(y_param)

X, y_command, y_param = create_sequences(df)

# ── 3. Train-validation split ──
X_train, X_val, y_command_train, y_command_val, y_param_train, y_param_val = train_test_split(
    X, y_command, y_param, test_size=0.2, random_state=42
)

# ── 4. Build model ──
inputs = Input(shape=(SEQ_LEN, 2))
x = LSTM(64)(inputs)
out_command = Dense(4, activation="softmax", name="command_output")(x)
out_param = Dense(1, activation="linear", name="param_output")(x)

model = Model(inputs=inputs, outputs=[out_command, out_param])
model.compile(
    optimizer="adam",
    loss={
        "command_output": "sparse_categorical_crossentropy",
        "param_output": "mse"
    },
    metrics={
        "command_output": SparseCategoricalAccuracy(name="accuracy"),
        "param_output": "mae"
    }
)

# ── 5. Train ──
model.fit(
    X_train,
    {"command_output": y_command_train, "param_output": y_param_train},
    validation_data=(X_val, {"command_output": y_command_val, "param_output": y_param_val}),
    epochs=12,
    batch_size=16
)

# fucking save the model
model.save("LSTM.h5")


# ── 6. Evaluate ──
y_pred_command_probs, y_pred_param = model.predict(X_val)
y_pred_command = np.argmax(y_pred_command_probs, axis=1)

# ── Classification Metrics ──
print("=== Classification Report ===")
print(classification_report(y_command_val, y_pred_command))

# Accuracy, Precision, Recall, F1
accuracy = accuracy_score(y_command_val, y_pred_command)
precision, recall, f1, _ = precision_recall_fscore_support(y_command_val, y_pred_command, average='weighted')

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# ROC-AUC
y_true_binarized = label_binarize(y_command_val, classes=[0, 1, 2, 3])
roc_auc = roc_auc_score(y_true_binarized, y_pred_command_probs, average='macro', multi_class='ovr')
print(f"ROC–AUC Score (OvR): {roc_auc:.4f}")

# ── Confusion Matrix ──
cm = confusion_matrix(y_command_val, y_pred_command)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

# ── ROC Curves ──
fpr = dict()
tpr = dict()
n_classes = 4
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_true_binarized[:, i], y_pred_command_probs[:, i])

plt.figure(figsize=(8, 6))
for i in range(n_classes):
    plt.plot(fpr[i], tpr[i], label=f"Class {i} ROC curve")
plt.plot([0, 1], [0, 1], 'k--')
plt.title("ROC Curves")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend(loc="lower right")
plt.grid()
plt.show()

# ── Param Output Similarity Score (Cosine) ──
from sklearn.metrics.pairwise import cosine_similarity
similarities = [
    dot(a, b) / (norm(a) * norm(b))
    for a, b in zip(y_pred_param.reshape(-1, 1), y_param_val.reshape(-1, 1))
]
avg_similarity = np.mean(similarities)
