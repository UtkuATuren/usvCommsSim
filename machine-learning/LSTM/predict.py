import numpy as np
import tensorflow as tf

# --- Configuration: adjust paths as needed ---
MODEL_PATH = "LSTM.h5"  # e.g. "cnn_timeseries_model"
SEQ_LEN = 5

# --- Mapping dicts ---
CMD_TO_CODE = {
    "move":     0,
    "turn":     1,
    "ascend":   2,
    "descend":  3
}
CODE_TO_CMD = {v: k for k, v in CMD_TO_CODE.items()}

# Given a raw parameter x (int), compute 1-based bin index:
#   bin 1 = [0–5), bin 2 = [5–10), bin 3 = [10–15), etc.
def param_to_bin(x: int) -> int:
    """Return 0-based bin index used during training (size-5 bins, clipped to 0–63)."""
    if x < 0:
        raise ValueError(f"Parameter must be ≥0, got {x}")
    idx = x // 5  # 0,1,2,…
    if idx > 63:
        idx = 63  # clip to max representable bin
    return idx

# Convert an integer (0–3) into 2-bit array [bit1, bit0]
def int_to_2bits(n: int) -> tuple:
    if not (0 <= n < 4):
        raise ValueError(f"Command code must be in [0..3], got {n}")
    return ((n >> 1) & 1, n & 1)

# Convert an integer (1..63 or whatever bin range) into 6-bit array [bit5..bit0]
def int_to_6bits(n: int) -> tuple:
    if n < 0 or n >= (1 << 6):
        raise ValueError(f"Param bin must be in [0..63], got {n}")
    return (
        (n >> 5) & 1,
        (n >> 4) & 1,
        (n >> 3) & 1,
        (n >> 2) & 1,
        (n >> 1) & 1,
        n & 1
    )

# Parse a single text command like "move 12"
def parse_text_command(text: str):
    parts = text.strip().lower().split()
    if len(parts) != 2:
        raise ValueError(f"Expected exactly 2 tokens (cmd, x), got: '{text}'")
    cmd_name, x_str = parts
    if cmd_name not in CMD_TO_CODE:
        raise ValueError(f"Unknown command '{cmd_name}' in '{text}'")
    try:
        x = int(x_str)
    except:
        raise ValueError(f"Parameter must be integer, got '{x_str}'")
    cmd_code = CMD_TO_CODE[cmd_name]
    bin_index = param_to_bin(x)
    return cmd_code, bin_index

# Build the 5×9 feature‐matrix for the model input
def build_input_matrix(text_cmds: list[str]) -> np.ndarray:
    """Return input array with shape (1, 5, 2) where each timestep has:
    [command_code (0–3), param_bin (0–63)].
    """
    if len(text_cmds) != SEQ_LEN:
        raise ValueError(f"You must supply exactly {SEQ_LEN} commands, got {len(text_cmds)}")

    mat = np.zeros((SEQ_LEN, 2), dtype=np.float32)
    for i, txt in enumerate(text_cmds):
        cmd_code, bin_idx = parse_text_command(txt)
        mat[i, 0] = cmd_code
        mat[i, 1] = bin_idx

    # Model expects shape (batch_size, 5, 2)
    return mat.reshape((1, SEQ_LEN, 2))

# Load your trained model (the bastard better exist)
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# Predict next command & parameter bin
def predict_next(text_cmds: list[str]) -> tuple[str,int]:
    """
    text_cmds: list of 5 strings, e.g. ["move 3", "turn 12", ...]
    Returns: (predicted_cmd_name, predicted_param_bin_idx)
    """
    x_mat = build_input_matrix(text_cmds)
    # model outputs two heads: [ cmd_probs, param_probs ]
    cmd_probs, param_pred = model.predict(x_mat)
    cmd_code_pred = int(np.argmax(cmd_probs[0]))
    # param_pred is a scalar in a 1-D array (linear output). Take first value and round.
    param_bin_pred = int(np.round(param_pred[0][0]))
    param_bin_pred = max(0, min(63, param_bin_pred))
    cmd_name_pred = CODE_TO_CMD[cmd_code_pred]
    return cmd_name_pred, param_bin_pred

if __name__ == "__main__":
    print("Enter the last 5 commands, one per line, in the format 'move 12', 'turn 7', etc.")
    user_cmds = []
    for i in range(1, SEQ_LEN + 1):
        txt = input(f"Command #{i}: ").strip()
        user_cmds.append(txt)

    try:
        cmd_pred, bin_pred = predict_next(user_cmds)
        print(f"\nPredicted next command: '{cmd_pred}', param bin: {bin_pred}")
        low = bin_pred * 5
        high = (bin_pred + 1) * 5
        print(f"(That corresponds to parameter roughly in [{low}, {high}) )")
    except Exception as e:
        print(f"Error: {e}")

