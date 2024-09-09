# inventory_optimization.py

import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data():
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

    # Create DataFrame
    df = pd.DataFrame(data)
    
    source_csv = "/data/source.csv"
    
    # Remove the existing output CSV file
    if os.path.exists(source_csv):
        os.remove(source_csv)
        
    # Save generated data to CSV    
    df.to_csv(source_csv, mode='a', header=not os.path.exists(source_csv), index=False)

    return df

def demand_forecasting(df):
    # Calculate rolling average demand
    df['DemandForecast'] = df.groupby('SKU')['SalesQuantity'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    return df

def classify_inventory(df):
    # Calculate coefficient of variation (CV) for demand variability
    cv_thresholds = [0.1, 0.3]  # Define thresholds for CV to classify SKUs
    df['CV'] = df.groupby('SKU')['SalesQuantity'].transform(lambda x: x.std() / x.mean())
    df['InventoryCategory'] = pd.cut(df['CV'], bins=[0, cv_thresholds[0], cv_thresholds[1], np.inf], labels=['A', 'B', 'C'])
    return df

def calculate_safety_stock(df):
    # Calculate safety stock levels
    service_level = 0.95  # Desired service level
    z_score = 1.96  # Z-score for 95% confidence interval
    df['SafetyStock'] = z_score * df.groupby('SKU')['SalesQuantity'].transform(lambda x: x.std())
    return df

def calculate_eoq(df):
    # Calculate Economic Order Quantity (EOQ)
    def calculate_eoq(demand, ordering_cost, holding_cost):
        return np.sqrt((2 * demand * ordering_cost) / holding_cost)

    ordering_cost = 100  # Cost of placing an order
    holding_cost = 5  # Cost of holding one unit in inventory
    df['EOQ'] = calculate_eoq(df['DemandForecast'], ordering_cost, holding_cost)
    return df

def calculate_reorder_point(df):
    # Calculate reorder point
    df['ReorderPoint'] = df['SafetyStock']
    # Implement dynamic adjustments based on inventory levels
    df['ReorderPoint'] += df.groupby('SKU')['InventoryLevel'].transform(lambda x: x.mean())
    return df

def main():
    # Step 1: Generate synthetic data
    df = generate_synthetic_data()

    # Step 2: Demand forecasting
    df = demand_forecasting(df)

    # Step 3: Inventory classification
    df = classify_inventory(df)

    # Step 4: Calculate safety stock
    df = calculate_safety_stock(df)

    # Step 5: Calculate Economic Order Quantity (EOQ)
    df = calculate_eoq(df)

    # Step 6: Calculate reorder point
    df = calculate_reorder_point(df)

    # Output final DataFrame
    print(df)

    # Save final data to CSV
    # df.to_csv(, index=False)
    output_csv = "/data/output.csv"
    
    # Remove the existing output CSV file
    if os.path.exists(output_csv):
        os.remove(output_csv)
        
    df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)


if __name__ == "__main__":
    main()
