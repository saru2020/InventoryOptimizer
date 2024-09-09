import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import os

# Generate synthetic data
np.random.seed(0)
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
date_range = pd.date_range(start_date, end_date, freq='D')

sku_list = ['SKU001', 'SKU002', 'SKU003']
data = {'Date': np.random.choice(date_range, size=1000),
        'SKU': np.random.choice(sku_list, size=1000),
        'SalesQuantity': np.random.randint(1, 20, size=1000),
        'InventoryLevel': np.random.randint(0, 100, size=1000)}

df = pd.DataFrame(data)

source_csv = "/data/source.csv"
    
# Remove the existing output CSV file
if os.path.exists(source_csv):
    os.remove(source_csv)
    
# Save generated data to CSV    
df.to_csv(source_csv, mode='a', header=not os.path.exists(source_csv), index=False)

# Handle missing values and outliers
# df.fillna(df.mean(), inplace=True)
df['Date'] = df['Date'].astype(int) // 10**9  # Convert datetime to Unix timestamp (seconds)
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

df = df[(np.abs(df['SalesQuantity'] - df['SalesQuantity'].mean()) <= (3 * df['SalesQuantity'].std()))]

# Encode categorical variables
sku_encoder = pd.get_dummies(df['SKU'])
df = pd.concat([df, sku_encoder], axis=1)
df.drop('SKU', axis=1, inplace=True)

# Split data into training and testing sets
X = df.drop(['SalesQuantity'], axis=1)
y = df['SalesQuantity']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a random forest regressor for demand forecasting
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate the model
y_pred = rf_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse:.2f}')

# Use the trained model for demand forecasting
df['DemandForecast'] = rf_model.predict(X)

# Classify inventory using k-means clustering
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['InventoryCategory'] = kmeans.fit_predict(df[['DemandForecast', 'InventoryLevel']])

# Calculate safety stock using the Newsvendor Model
def calculate_safety_stock(demand, lead_time, service_level):
    z_score = 1.96  # 95% confidence interval
    safety_stock = z_score * np.sqrt(lead_time) * demand.std()
    return safety_stock

lead_time = 7  # days
service_level = 0.95
# df['SafetyStock'] = df.apply(lambda row: calculate_safety_stock(row['DemandForecast'], lead_time, service_level), axis=1)
df['SafetyStock'] = calculate_safety_stock(df['DemandForecast'], lead_time, service_level)

# Calculate EOQ using the Economic Order Quantity formula
def calculate_eoq(demand, ordering_cost, holding_cost):
    eoq = np.sqrt((2 * demand * ordering_cost) / holding_cost)
    return eoq

ordering_cost = 100  # cost of placing an order
holding_cost = 5  # cost of holding one unit in inventory
df['EOQ'] = df.apply(lambda row: calculate_eoq(row['DemandForecast'], ordering_cost, holding_cost), axis=1)

# Calculate reorder point using the Reorder Point with Lead Time formula
def calculate_reorder_point(safety_stock, lead_time, eoq):
    reorder_point = safety_stock + (eoq / lead_time)
    return reorder_point

df['ReorderPoint'] = df.apply(lambda row: calculate_reorder_point(row['SafetyStock'], lead_time, row['EOQ']), axis=1)

print('results - df: ', df)

# Visualize the results
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['DemandForecast'], label='Demand Forecast')
plt.plot(df['Date'], df['SalesQuantity'], label='Actual Sales')
plt.xlabel('Date')
plt.ylabel('Sales Quantity')
plt.title('Demand Forecasting')
plt.legend()
plt.savefig('/data/_plot_.png')
plt.show()

output_csv = "/data/output.csv"

# Remove the existing output CSV file
if os.path.exists(output_csv):
    os.remove(output_csv)
    
df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)