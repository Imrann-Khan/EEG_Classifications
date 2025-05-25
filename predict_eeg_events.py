import numpy as np
import pandas as pd
from collections import Counter
from tensorflow.keras.models import load_model
import os

N_CH = 55
WINDOW_SIZE = 5
STEP = 2
label_to_code = {0:1, 1:2, 2:5, 3:6}

def make_windows(epoch, window=WINDOW_SIZE, step=STEP):
    n_ch, n_t = epoch.shape
    data = epoch.T 
    Xw = []
    for start in range(0, n_t - window + 1, step):
        Xw.append(data[start:start+window, :])
    return np.stack(Xw, axis=0).astype('float32')

def predict_event(model, epoch):
    ep = epoch.astype('float32').reshape(1, N_CH, -1) 
    Xw = make_windows(ep[0])                           
    probs = model.predict(Xw, verbose=0)                
    preds = probs.argmax(axis=1)                         
    top = Counter(preds).most_common(1)[0][0]           
    return label_to_code[top]

def main():

    model = load_model("my_gru_model.h5")
    saved_trials_dir = "saved_trials"

    for filename in os.listdir(saved_trials_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(saved_trials_dir, filename)
            df = pd.read_csv(filepath)
            if df.shape[1] != N_CH:
                print(f"Skipping {filename}: expected {N_CH} channels, got {df.shape[1]}")
                continue
            trial_data = df.values.T.astype(np.float32) 
            
            pred_event = predict_event(model, trial_data)
            print(f"File: {filename}, Predicted event code: {pred_event}")

if __name__ == "__main__":
    main()
