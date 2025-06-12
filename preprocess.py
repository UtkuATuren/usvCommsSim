import pandas as pd
import numpy as np
import sys

# === 0. CONFIGURE YOUR INPUT FILE PATH ===
input_filename = "commands.csv"  # ← adjust to your path
import pandas as pd
import numpy as np
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
df = pd.read_csv("/content/processed_commands.csv")
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
    epochs=10,
    batch_size=16
)


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
similarity = cosine_similarity(y_pred_param.reshape(-1, 1), y_param_val.reshape(-1, 1))
avg_similarity = np.mean(np.diag(similarity))
print(f"Cosine Similarity (Param): {avg_similarity:.4f}")
# === 1. LOAD AND INSPECT HEADER ===
try:
    df = pd.read_csv(input_filename, sep=None, engine="python")
except Exception as e:
    print(f"Error loading '{input_filename}': {e}")
    sys.exit(1)

print("Detected columns in the file:", df.columns.tolist())

# === 2. CHECK FOR EXPECTED COLUMNS ===
expected_cols = ["tick", "event_type", "success", "command", "command_param", "command_lost"]
missing = [c for c in expected_cols if c not in df.columns]
if missing:
    print(f"Error: Missing columns: {missing}")
    sys.exit(1)

# === 3. KEEP ONLY RELEVANT COLUMNS ===
keep_cols = ["tick", "event_type", "success", "command", "command_param", "command_lost"]
df = df[keep_cols].copy()

# === 4. VALIDATE 'command' VALUES ===
expected_commands = {"MOVE", "TURN", "ASCEND", "DESCEND"}
unique_commands = set(df["command"].dropna().unique())
unexpected = unique_commands - expected_commands
if unexpected:
    print(f"Warning: Unexpected command values: {unexpected}")

# === 5. MAP 'command' → 0–3 ===
command_mapping = {"MOVE": 0, "TURN": 1, "ASCEND": 2, "DESCEND": 3}
df["command_idx"] = df["command"].map(command_mapping)
if df["command_idx"].isna().any():
    print("Warning: Some 'command' entries couldn’t be mapped; they’ll be treated as 0.")

# === 6. SPLIT 'command_idx' INTO TWO BITS ===
df["command_bit1"] = df["command_idx"].fillna(0).astype(int).apply(lambda x: (x >> 1) & 1)
df["command_bit0"] = df["command_idx"].fillna(0).astype(int).apply(lambda x: x & 1)

# === 7. BIN 'command_param' INTO SIZE-5 RANGES → 0–63 INDEX ===
def param_to_bin_index(val):
    try:
        idx = int(np.floor(val / 5))
    except Exception:
        idx = 0
    if idx < 0:
        idx = 0
    if idx >= 64:
        print(f"Warning: parameter {val} out of range; clipping to 63.")
        idx = 63
    return idx

df["param_bin_idx"] = df["command_param"].apply(param_to_bin_index)

# === 8. CONVERT 'param_bin_idx' → 6 BITS (param_bit5…param_bit0) ===
for bit_pos in range(6):
    df[f"param_bit{5 - bit_pos}"] = df["param_bin_idx"].apply(lambda idx: (idx >> (5 - bit_pos)) & 1)

# === 9. CONVERT 'success' & 'command_lost' TO FLAGS (fill NaN first) ===
df["success_flag"] = df["success"].fillna(False).astype(int)
df["lost_flag"]    = df["command_lost"].fillna(False).astype(int)

# === 10. FILTER ONLY event_type=="command" ===
df_commands = df[df["event_type"] == "command"].copy()

# === 11. BUILD FINAL DATAFRAME ===
final_cols = [
    "tick",
    "event_type",
    "success_flag",
    "command_bit1",
    "command_bit0",
    "param_bit5",
    "param_bit4",
    "param_bit3",
    "param_bit2",
    "param_bit1",
    "param_bit0",
    "lost_flag"
]
processed_df = df_commands[final_cols]

# === 12. SAVE TO CSV ===
output_filename = "processed_commands.csv"
processed_df.to_csv(output_filename, index=False)
print(f"Preprocessing complete. Output saved to '{output_filename}'.")
