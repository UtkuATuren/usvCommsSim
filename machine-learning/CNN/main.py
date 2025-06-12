import numpy as np
import pandas as pd
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Conv1D, GlobalAveragePooling1D,
                                     Dense)
from tensorflow.keras.optimizers import Adam

# 1. Load & preprocess
df = pd.read_csv("processed_commands_3.csv")

# Drop unwanted cols
df = df.drop(columns=["event_type", "lost_flag"])

# Compute integer labels
df["command"] = df["command_bit1"]*2 + df["command_bit0"]
df["param"]   = (
    df["param_bit5"]*32 + df["param_bit4"]*16 +
    df["param_bit3"]*8  + df["param_bit2"]*4  +
    df["param_bit1"]*2  + df["param_bit0"]
)

# Features = success_flag + the raw bits
feat_cols = ["success_flag",
             "command_bit1","command_bit0",
             "param_bit5","param_bit4","param_bit3",
             "param_bit2","param_bit1","param_bit0"]
X_raw = df[feat_cols].values
y_cmd = df["command"].values
y_param = df["param"].values

# 2. Create sequences of length 5
SEQ_LEN = 12
X, yc, yp = [], [], []
for i in range(len(df) - SEQ_LEN):
    X.append(X_raw[i:i+SEQ_LEN])
    yc.append(y_cmd[i+SEQ_LEN])
    yp.append(y_param[i+SEQ_LEN])
X = np.array(X)                  # shape = (n_samples, 5, 9)
yc = np.array(yc)                # shape = (n_samples,)
yp = np.array(yp)

# 3. Build the 1D‐CNN
n_commands = len(np.unique(yc))  # usually 4
n_params   = len(np.unique(yp))  # up to 64

inp = Input(shape=(SEQ_LEN, X.shape[2]))
x = Conv1D(32, 3, activation="relu", padding="same")(inp)
x = Conv1D(32, 3, activation="relu", padding="same")(x)
x = GlobalAveragePooling1D()(x)

cmd_out   = Dense(n_commands, activation="softmax", name="cmd")(x)
param_out = Dense(n_params,   activation="softmax", name="param")(x)

model = Model(inputs=inp, outputs=[cmd_out, param_out])
model.compile(
    optimizer=Adam(1e-3),
    loss={
        "cmd":   "sparse_categorical_crossentropy",
        "param": "sparse_categorical_crossentropy"
    },
    metrics={
        "cmd":   "accuracy",
        "param": "accuracy"
    }
)

model.summary()

# 4. Train the damn thing
history = model.fit(
    X, {"cmd": yc, "param": yp},
    epochs=15,
    batch_size=32,
    validation_split=0.2
)

model.save("cnn-model-12.keras")

from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_fscore_support, accuracy_score
)
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Predict
y_pred_cmd_probs, y_pred_param_probs = model.predict(X)
y_pred_cmd   = np.argmax(y_pred_cmd_probs, axis=1)
y_pred_param = np.argmax(y_pred_param_probs, axis=1)

# === Command Classification Metrics ===
print("=== Classification Report: Command ===")
print(classification_report(yc, y_pred_cmd))

accuracy = accuracy_score(yc, y_pred_cmd)
precision, recall, f1, _ = precision_recall_fscore_support(yc, y_pred_cmd, average='weighted')
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# === Confusion Matrix ===
cm = confusion_matrix(yc, y_pred_cmd)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title("Command Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

# === ROC-AUC ===
yc_binarized = label_binarize(yc, classes=np.unique(yc))
roc_auc = roc_auc_score(yc_binarized, y_pred_cmd_probs, average='macro', multi_class='ovr')
print(f"ROC–AUC Score (OvR): {roc_auc:.4f}")

# === ROC Curves ===
fpr = dict()
tpr = dict()
n_classes = yc_binarized.shape[1]
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(yc_binarized[:, i], y_pred_cmd_probs[:, i])

plt.figure(figsize=(8,6))
for i in range(n_classes):
    plt.plot(fpr[i], tpr[i], label=f"Class {i}")
plt.plot([0, 1], [0, 1], 'k--')
plt.title("Command ROC Curves")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend(loc="lower right")
plt.grid()
plt.show()

# === Cosine Similarity for Params ===
from numpy.linalg import norm
from numpy import dot

param_similarities = [
    dot([a], [b]) / (norm([a]) * norm([b]))
    for a, b in zip(y_pred_param, yp)
]
print(f"Average Cosine Similarity (Params): {np.mean(param_similarities):.4f}")
