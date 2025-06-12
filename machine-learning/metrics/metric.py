import numpy as np
import pandas as pd
import gc
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
import tensorflow as tf

# 1. Load data & compute command/param codes
df = pd.read_csv("processed_commands.csv")
df["command"] = df["command_bit1"] * 2 + df["command_bit0"]
df["param"] = (
    df["param_bit5"]*32 + df["param_bit4"]*16 +
    df["param_bit3"]*8  + df["param_bit2"]*4  +
    df["param_bit1"]*2  + df["param_bit0"]
)

# 2. Create stratified validation indices
indices = df.index.values
commands = df["command"].values
_, val_idx, _, _ = train_test_split(
    indices, commands, test_size=0.2,
    random_state=42, stratify=commands
)

# 3. Batch‐streaming evaluation generator
def eval_stream(model, seq_len, feat_cols, val_idx,
                batch_size=2048, predict_batch=256):
    all_y, all_pred, all_prob, all_ptrue, all_ppred = [], [], [], [], []
    for start in range(0, len(val_idx), batch_size):
        batch = val_idx[start:start+batch_size]
        Xb, yb, pb = [], [], []
        for i in batch:
            if i + seq_len < len(df):
                Xb.append(df.iloc[i:i+seq_len][feat_cols].values)
                yb.append(df.iloc[i+seq_len]["command"])
                pb.append(df.iloc[i+seq_len]["param"])
        if not Xb:
            continue
        Xb = np.array(Xb, dtype=np.float32)
        probs, params = model.predict(Xb, batch_size=predict_batch, verbose=0)
        preds = np.argmax(probs, axis=1)
        # param predictions: regression -> round; classification -> argmax
        if params.ndim == 2 and params.shape[1] == 1:
            p_pred = np.clip(np.round(params).astype(int).flatten(), 0, 63)
        else:
            p_pred = np.argmax(params, axis=1)
        all_y.extend(yb)
        all_pred.extend(preds)
        all_prob.extend(probs)
        all_ptrue.extend(pb)
        all_ppred.extend(p_pred)
        del Xb, yb, pb, probs, params, preds, p_pred
        gc.collect()
    return (np.array(all_y),
            np.array(all_pred),
            np.vstack(all_prob),
            np.array(all_ptrue),
            np.array(all_ppred))

# 4. Load models
lstm_model = tf.keras.models.load_model(
    "LSTM.h5",
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()},
    compile=False
)
# **Use the 12-length CNN model file and correct name**
cnn_model = tf.keras.models.load_model(
    "cnn-model.keras",
    compile=False
)

# 5. Define feature columns
lstm_feats = ["command", "param"]
cnn_feats  = ["success_flag", "command_bit1", "command_bit0"] + \
             [f"param_bit{b}" for b in range(5, -1, -1)]

# 6a. Evaluate LSTM (seq_len=5)
l_y, l_pred, l_prob, l_ptrue, l_ppred = eval_stream(
    lstm_model,
    seq_len=5,
    feat_cols=lstm_feats,
    val_idx=val_idx
)

# 6b. Evaluate CNN (seq_len=5)
c_y, c_pred, c_prob, c_ptrue, c_ppred = eval_stream(
    cnn_model,
    seq_len=5,
    feat_cols=cnn_feats,
    val_idx=val_idx
)

# 7. Command‐classification metrics
def cmd_metrics(y, pred, prob):
    y_bin = label_binarize(y, classes=np.unique(commands))
    acc = accuracy_score(y, pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y, pred, average="weighted"
    )
    roc = roc_auc_score(y_bin, prob, average="macro", multi_class="ovr")
    cm = confusion_matrix(y, pred)
    return acc, prec, rec, f1, roc, cm

l_metrics = cmd_metrics(l_y, l_pred, l_prob)
c_metrics = cmd_metrics(c_y, c_pred, c_prob)

# 8. Parameter‐recovery similarity
def param_stats(true, pred):
    diffs = np.abs(true - pred)
    return {
        "MAE_bins": np.mean(diffs),
        "Within±1": np.mean(diffs <= 1),
        "Within±2": np.mean(diffs <= 2)
    }

l_param_stats = param_stats(l_ptrue, l_ppred)
c_param_stats = param_stats(c_ptrue, c_ppred)

# 9. Print summary tables
cmd_df = pd.DataFrame({
    "LSTM": {
        "Accuracy":  l_metrics[0],
        "Precision": l_metrics[1],
        "Recall":    l_metrics[2],
        "F1 Score":  l_metrics[3],
        "ROC-AUC":   l_metrics[4]
    },
    "CNN": {
        "Accuracy":  c_metrics[0],
        "Precision": c_metrics[1],
        "Recall":    c_metrics[2],
        "F1 Score":  c_metrics[3],
        "ROC-AUC":   c_metrics[4]
    }
}).T

print("=== Command Classification Metrics ===")
print(cmd_df)

param_df = pd.DataFrame({
    "LSTM": l_param_stats,
    "CNN":  c_param_stats
}).T

print("\n=== Parameter Recovery Similarity ===")
print(param_df)

# 10. Plot confusion matrices
for name, m in zip(["LSTM", "CNN"], [l_metrics, c_metrics]):
    cm = m[5]
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"{name} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.show()
