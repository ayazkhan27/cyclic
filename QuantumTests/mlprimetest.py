import math
import numpy as np
import sympy
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from quantumcomparisonpt3 import get_reptend_sequence

# Known full reptend primes
full_reptend_primes = [
    7, 17, 19, 23, 29, 47, 59, 61, 97, 109, 113,
    131, 149, 167, 179, 181, 193, 223, 229, 233,
    257, 263, 269, 313, 337, 367, 379, 383, 389,
    419, 433, 461, 487, 491, 499, 503, 509, 541,
    571, 577, 593, 619, 647, 659, 701, 709, 727,
    743, 811, 821, 823, 857, 863, 887, 937, 941,
    953, 971, 977, 983, 1019, 1021, 1033, 1051
]

# Generate a list of prime numbers up to a certain limit
prime_limit = 2000
primes = list(sympy.primerange(2, prime_limit))

# Label primes: 1 for full reptend primes, 0 for others
labels = [1 if p in full_reptend_primes else 0 for p in primes]

# Feature: Length of repeating decimal sequence of 1/p
def repeating_decimal_length(p):
    sequence = get_reptend_sequence(p)
    return len(sequence)

# Feature: Check if 10 is a primitive root modulo p
def is_primitive_root_10(p):
    # Ensure that 10 and p are relatively prime
    if math.gcd(10, p) != 1:
        return False  # Not relatively prime, so cannot be a primitive root
    return sympy.is_primitive_root(10, p)

# Construct feature matrix
features = []
for p in primes:
    repeat_len = repeating_decimal_length(p)
    primitive_root = is_primitive_root_10(p)
    features.append([repeat_len, primitive_root])

# Convert to numpy arrays
X = np.array(features)
y = np.array(labels)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate model using cross-validation
cv_scores = cross_val_score(clf, X, y, cv=5)
print(f"Cross-validation Accuracy: {np.mean(cv_scores):.2f} ± {np.std(cv_scores):.2f}")

# Predict on the test set
y_pred = clf.predict(X_test)

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Non-Reptend', 'Reptend']))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

# Feature importance
feature_names = ['Repeating Decimal Length', 'Is Primitive Root 10']
importances = clf.feature_importances_
indices = np.argsort(importances)[::-1]
print("\nFeature Importances:")
for idx in indices:
    print(f"{feature_names[idx]}: {importances[idx]:.4f}")
