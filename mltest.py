import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine

# ----------------------------------------
# Step 1: Neural Network Model Definition
# ----------------------------------------

class TradeClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(TradeClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return self.softmax(x)

# ----------------------------------------
# Step 2: Data Preparation
# ----------------------------------------

def preprocess_data(file_path):
    # Load data
    data = pd.read_csv(file_path)

    # Feature engineering
    data['price_change'] = data['close'].pct_change()*100.0
    data['volume_change'] = data['volume'].pct_change()
    data = data.dropna()

    # Define features and labels
    features = ['open', 'high', 'low', 'close', 'volume', 'price_change', 'volume_change']
    X = data[features]
    y = pd.cut(data['price_change'], bins=[-np.inf, -0.01, 0.01, np.inf], labels=[0, 1, 2]).astype(int)

    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    return X, y, scaler

# ----------------------------------------
# Step 3: Model Training
# ----------------------------------------

def train_model(X_train, y_train, input_size, num_classes):
    # Convert data to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train.values, dtype=torch.long)  # Ensure integer type

    # Debugging to verify label values
    print("Unique y_train values:", torch.unique(y_train))
    assert y_train.min() >= 0 and y_train.max() < num_classes, \
        f"Target labels out of range. Expected 0 to {num_classes - 1}, got {y_train.unique()}"

    # Initialize model, loss function, and optimizer
    model = TradeClassifier(input_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    num_epochs = 50
    for epoch in range(num_epochs):
        # Forward pass
        outputs = model(X_train)
        loss = criterion(outputs, y_train)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    return model, optimizer

# ----------------------------------------
# Step 4: Save and Load Model Weights
# ----------------------------------------

import json

def save_model_to_db(model, db_url, table_name='model_weights'):
    engine = create_engine(db_url)
    weights = {name: param.detach().numpy().tolist() for name, param in model.state_dict().items()}
    data = [{'name': name, 'weight': json.dumps(weight)} for name, weight in weights.items()]  # Serialize as JSON strings
    df = pd.DataFrame(data)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print("Model weights saved to database.")

def load_model_from_db(model, db_url, table_name='model_weights'):
    engine = create_engine(db_url)
    df = pd.read_sql(table_name, engine)
    state_dict = {
        row['name']: torch.tensor(json.loads(row['weight']))  # Deserialize JSON strings back to lists
        for _, row in df.iterrows()
    }
    model.load_state_dict(state_dict)
    print("Model weights loaded from database.")

# ----------------------------------------
# Step 5: Incorporate Feedback
# ----------------------------------------

def incorporate_feedback(X_feedback, y_feedback, model, optimizer, scaler):
    # Preprocess feedback data
    X_feedback = scaler.transform(X_feedback)
    X_feedback = torch.tensor(X_feedback, dtype=torch.float32)
    y_feedback = torch.tensor(y_feedback.values, dtype=torch.long)

    # Fine-tune model on feedback
    model.train()
    criterion = nn.CrossEntropyLoss()
    outputs = model(X_feedback)
    loss = criterion(outputs, y_feedback)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print("Model updated with feedback.")

# ----------------------------------------
# Step 6: Real-Time Prediction
# ----------------------------------------

def predict_live(model, scaler, live_data):
    # Preprocess live data
    live_data['price_change'] = live_data['close'].pct_change()
    live_data['volume_change'] = live_data['volume'].pct_change()
    live_data = live_data.dropna()

    features = ['open', 'high', 'low', 'close', 'volume', 'price_change', 'volume_change']
    X_live = scaler.transform(live_data[features])
    X_live = torch.tensor(X_live, dtype=torch.float32)

    # Predict probabilities
    model.eval()
    with torch.no_grad():
        predictions = model(X_live)
    return torch.argmax(predictions, dim=1)






import matplotlib.pyplot as plt
import pandas as pd
import torch

def plot_historical_trades_with_ml(data, model, num_classes):
    """
    Plot historical trades with ML-learned entry, stop loss, and target levels.

    Args:
        data (pd.DataFrame): Historical OHLCV data.
        model (torch.nn.Module): The trained ML model.
        num_classes (int): Number of classes for trade classifications (e.g., 3 for A+, A, B).
    """

        # Load data
    historical_file ='D:\\py_code_workspace\\OutFiles\\niftyData.csv'
    data = pd.read_csv(historical_file)
    data = data.drop(columns=['symbol'])

    # Feature engineering
    data['price_change'] = data['close'].pct_change()*10.0
    data['volume_change'] = data['volume'].pct_change()
    data = data.dropna()

    # Convert Date to datetime
    data['Date'] = pd.to_datetime(data['datetime'])
    # Drop non-numeric columns
    numeric_data = data.drop(columns=['Date','datetime', 'close'])  # Ensure no non-numeric columns are present
    print(numeric_data.head())
    X = torch.tensor(numeric_data.values, dtype=torch.float32) 
    outputs = model(X)
    predictions = torch.argmax(outputs, dim=1).numpy()

    # Map predictions to classes
    classes = ['C'] + [chr(ord('A') + i) for i in range(num_classes - 1)]

    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'], data['close'], label='Close Price')

    for idx, date in enumerate(data['Date']):
        prediction = predictions[idx]
        classification = classes[prediction]

        # Entry, Stop Loss, Target levels
        entry = date
        sl = date + pd.Timedelta(days=1)  # Example stop loss: next day
        target = date + pd.Timedelta(days=2)  # Example target: day after next

        # Plot entry, stop loss, and target
        plt.scatter(entry, data.loc[data['Date'] == entry, 'Close'].values, color='green', label=f'Entry {classification}')
        plt.scatter(sl, data.loc[data['Date'] == sl, 'Close'].values, color='red', label=f'Stop Loss {classification}')
        plt.scatter(target, data.loc[data['Date'] == target, 'Close'].values, color='blue', label=f'Target {classification}')

    plt.title('Historical Trades with ML-Learned Entry, SL, and Target Levels')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()




# ----------------------------------------
# Step 7: Main Function
# ----------------------------------------

def main():
    # File paths and database URL
    historical_file ='D:\\py_code_workspace\\OutFiles\\niftyData.csv'
    db_url = "sqlite:///model_weights.db"

    # Preprocess data
    X, y, scaler = preprocess_data(historical_file)
    input_size = X.shape[1]
    num_classes = len(np.unique(y))

    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model, optimizer = train_model(X_train, y_train, input_size, num_classes)

    # Save model weights
    save_model_to_db(model, db_url)

    # Load model weights
    load_model_from_db(model, db_url)

    # Simulate feedback
    feedback_data = X_test[:10]  # Simulated feedback data
    feedback_labels = y_test[:10]  # Simulated feedback labels
    incorporate_feedback(feedback_data, feedback_labels, model, optimizer, scaler)

    # # Real-time prediction
    # live_data = pd.read_csv('live_ohlcv.csv')
    # predictions = predict_live(model, scaler, live_data)
    # print("Predictions:", predictions)
    
    # Example usage
    # Assuming model and num_classes are defined
    plot_historical_trades_with_ml(data=[], model=model, num_classes=3)


# ----------------------------------------
# Run the Main Function
# ----------------------------------------



if __name__ == "__main__":
    main()


