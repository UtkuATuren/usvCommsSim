import random
import numpy as np
import pandas as pd

# === Load & prepare data ===
df = pd.read_csv("processed_commands.csv")  # must be in time order
SEQ_LEN = 5
NUM_TESTS = 20  # keep it low if you want readable output

def get_label_tuple(row):
    return (int(row["command"]), int(row["param"]))

X_test = []
y_true = []
y_pred = []

print("\n=== MODEL PREDICTION RESULTS ===\n")

for i in range(NUM_TESTS):
    idx = random.randint(0, len(df) - SEQ_LEN - 1)
    sequence_df = df.iloc[idx : idx + SEQ_LEN]
    target_row = df.iloc[idx + SEQ_LEN]

    input_seq = sequence_df[["command", "param"]].to_numpy()
    input_seq = np.expand_dims(input_seq, axis=0)  # (1, seq_len, 2)

    # === Predict ===
    prediction = model.predict(input_seq)

    # Assume model has two outputs: command and param
    if isinstance(prediction, list) and len(prediction) == 2:
        cmd_pred = np.argmax(prediction[0], axis=-1)[0]
        param_pred = np.argmax(prediction[1], axis=-1)[0]
    else:
        # If model has single output combining command + param
        # (e.g. 4*64 = 256 class space), you'll need to map index -> (cmd, param)
        raise NotImplementedError("Model output format not supported here")

    # === True label ===
    true_cmd, true_param = get_label_tuple(target_row)

    # === Print results ===
    print(f"[{i+1}]")
    print("Input Sequence:", [get_label_tuple(row) for _, row in sequence_df.iterrows()])
    print("True Next:     ", (true_cmd, true_param))
    print("Predicted:     ", (cmd_pred, param_pred))
    if (cmd_pred == true_cmd) and (param_pred == true_param):
        print("✅ Correct\n")
    else:
        print("❌ WRONG\n")