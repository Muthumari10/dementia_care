import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# Dataset Columns
# -------------------------
columns = ['age','gender','blood_pressure','cholesterol','stress_level','depression_level',
           'alcohol_consumption','smoking_habit','academic_performance','sleep_quality',
           'internet_addiction','physical_activity','dementia_result']

data = pd.read_csv('dementia_dataset.csv', header=None, names=columns)

# Strip whitespace & handle None
for col in data.select_dtypes(include='object').columns:
    data[col] = data[col].str.strip()

# Replace 'None' with 'Unknown' in categorical columns
cat_cols = ['gender','blood_pressure','stress_level','depression_level',
            'alcohol_consumption','smoking_habit','academic_performance',
            'sleep_quality','internet_addiction','physical_activity']

for col in cat_cols:
    data[col] = data[col].fillna('Unknown')
    data[col] = data[col].replace('None','Unknown')

# Encode categorical columns
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    encoders[col] = le

# Encode target
data['dementia_result'] = data['dementia_result'].map({'Yes':1, 'No':0})

# Ensure numeric columns
numeric_cols = ['age','cholesterol']
data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors='coerce')
data = data.dropna()

# Features & target
X = data.drop('dementia_result', axis=1)
y = data['dementia_result']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------
# Train Model with progressive accuracy tracking
# -------------------------
n_estimators_list = [10, 50, 100, 150, 200]
train_acc = []
test_acc = []

for n in n_estimators_list:
    model = RandomForestClassifier(n_estimators=n, random_state=42)
    model.fit(X_train, y_train)
    train_acc.append(model.score(X_train, y_train))
    test_acc.append(model.score(X_test, y_test))

# Train final model with full n_estimators
final_model = RandomForestClassifier(n_estimators=200, random_state=42)
final_model.fit(X_train, y_train)

# -------------------------
# Plot Accuracy Graph
# -------------------------
plt.figure(figsize=(8,5))
plt.plot(n_estimators_list, train_acc, label='Training Accuracy', marker='o')
plt.plot(n_estimators_list, test_acc, label='Test Accuracy', marker='s')
plt.title('Random Forest Accuracy vs Number of Trees')
plt.xlabel('Number of Trees')
plt.ylabel('Accuracy')
plt.ylim(0,1)
plt.grid(True)
plt.legend()
plt.savefig('static/accuracy_plot.png')
plt.close()

# -------------------------
# Plot Feature Importance
# -------------------------
importances = final_model.feature_importances_
features = X.columns

plt.figure(figsize=(10,6))
plt.barh(features, importances, color='skyblue')
plt.xlabel('Importance')
plt.title('Feature Importance in Dementia Prediction')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('static/feature_importance.png')
plt.close()

print("Feature importance chart saved successfully!")

# -------------------------
# Save Model and Encoders
# -------------------------
joblib.dump(final_model, 'dementia_model.pkl')
joblib.dump(encoders, 'dementia_encoders.pkl')
print("Final model, encoders, and accuracy graph saved successfully!")
