import numpy as np
import pandas as pd
from collections import Counter
from tensorflow.keras.models import load_model
import os
import serial
import time

# Define the parameters for the EEG data
N_CH = 55
WINDOW_SIZE = 5
STEP = 2
label_to_code = {0:1, 1:2, 2:5, 3:6}


arduino = serial.Serial('COM3', 9600)
time.sleep(2) 

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


def send_command(command):
    arduino.write(f"{command}\n".encode())

def send_arduino_command(event_code):
    """Send corresponding command to Arduino based on event prediction."""
    if event_code == 1:
        send_command("elbow_flexion")  # Elbow flexion
        time.sleep(1)
    elif event_code == 2:
        send_command("elbow_extension")  # Elbow extension
        time.sleep(1)
    elif event_code == 5:
        send_command("hand_close")  # Hand close
        time.sleep(1)
    elif event_code == 6:
        send_command("hand_open")  # Hand open
        time.sleep(1)
    else:
        print(f"Unknown event code: {event_code}")

def main():
    model = load_model("my_gru_model.h5")  
    saved_trials_dir = "saved_trials"

    filename = "event_code_2_trial.csv" 
    filepath = os.path.join(saved_trials_dir, filename)

    if not os.path.exists(filepath):
        print(f"File {filename} does not exist in directory {saved_trials_dir}")
        return

    df = pd.read_csv(filepath)
    if df.shape[1] != N_CH:
        print(f"Skipping {filename}: expected {N_CH} channels, got {df.shape[1]}")
        return

    trial_data = df.values.T.astype(np.float32) 
    
    # Predict the event based on the EEG data
    pred_event = predict_event(model, trial_data)
    print(f"File: {filename}, Predicted event code: {pred_event}")
    send_arduino_command(pred_event)



if __name__ == "__main__":
    main()
