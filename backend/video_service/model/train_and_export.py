import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# load training data
df = pd.read_csv("shots_metrics.csv")
X = df.drop(columns=["video_name", "shooting_arm", "y"])
y = df["y"]

# train model
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(
  n_estimators=200,
  max_depth=15,
  class_weight="balanced",
  random_state=42
)
model.fit(X_scaled, y)

# export
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(list(X.columns), 'feature_columns.pkl')
