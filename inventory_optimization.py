# inventory_optimization.py

import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays

def generate_synthetic_data():
    # Generate synthetic data with Tamil Nadu holidays
    np.random.seed(0)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')

    sku_list = ['SKU001', 'SKU002', 'SKU003']
    store_list = ['Store001', 'Store002', 'Store003']
    tamil_nadu_holidays = holidays.IN(state='TN', years=[2023])

    data = []
    for date in date_range:
        for store in store_list:
            for sku in sku_list:
                sales_quantity = np.random.randint(1, 20)
                if date in tamil_nadu_holidays:
                    sales_quantity += 10  # Increase sales quantity on holidays
                inventory_level = np.random.randint(0, 100)
                data.append([date, store, sku, sales_quantity, inventory_level])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Store', 'SKU', 'SalesQuantity', 'InventoryLevel'])
    
    source_csv = "/data/source.csv"
    
    # Remove the existing output CSV file
    if os.path.exists(source_csv):
        os.remove(source_csv)
        
    # Save generated data to CSV    
    df.to_csv(source_csv, mode='a', header=not os.path.exists(source_csv), index=False)

    return df

def demand_forecasting(df):
    # Calculate rolling average demand
    df['DemandForecast'] = df.groupby(['Store', 'SKU'])['SalesQuantity'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    return df

def classify_inventory(df):
    # Calculate coefficient of variation (CV) for demand variability
    cv_thresholds = [0.1, 0.3]  # Define thresholds for CV to classify SKUs
    df['CV'] = df.groupby(['Store', 'SKU'])['SalesQuantity'].transform(lambda x: x.std() / x.mean())
    df['InventoryCategory'] = pd.cut(df['CV'], bins=[0, cv_thresholds[0], cv_thresholds[1], np.inf], labels=['A', 'B', 'C'])
    return df

def calculate_safety_stock(df):
    # Calculate safety stock levels
    service_level = 0.95  # Desired service level
    z_score = 1.96  # Z-score for 95% confidence interval
    df['SafetyStock'] = z_score * df.groupby(['Store', 'SKU'])['SalesQuantity'].transform(lambda x: x.std())
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
    df['ReorderPoint'] += df.groupby(['Store', 'SKU'])['InventoryLevel'].transform(lambda x: x.mean())
    return df

def should_reorder(df):
    # Determine if the stock should be reordered
    df['Reorder'] = df['InventoryLevel'] < df['ReorderPoint']
    return df

def calculate_daily_order(df):
    # Calculate daily order quantities for each store
    df['OrderQuantity'] = df.apply(lambda row: max(row['ReorderPoint'] - row['InventoryLevel'], 0) if row['Reorder'] else 0, axis=1)
    return df

def calculate_inventory_turnover(df):
    # Calculate inventory turnover ratio
    df['TotalSales'] = df.groupby(['Store', 'SKU'])['SalesQuantity'].transform('sum')
    df['AverageInventoryLevel'] = df.groupby(['Store', 'SKU'])['InventoryLevel'].transform('mean')
    df['InventoryTurnover'] = df['TotalSales'] / df['AverageInventoryLevel']
    return df

def calculate_inventory_turnover_store(df):
    # Calculate inventory turnover ratio at the store level
    store_sales = df.groupby('Store')['SalesQuantity'].sum().reset_index()
    store_inventory = df.groupby('Store')['InventoryLevel'].mean().reset_index()
    store_turnover = pd.merge(store_sales, store_inventory, on='Store')
    store_turnover['InventoryTurnover'] = store_turnover['SalesQuantity'] / store_turnover['InventoryLevel']
    return store_turnover

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

    # Step 7: Determine if the stock should be reordered
    df = should_reorder(df)

    # Step 8: Calculate daily order quantities for each store
    df = calculate_daily_order(df)

    # Step 9: Calculate inventory turnover ratio
    df = calculate_inventory_turnover(df)

    # Step 10: Calculate inventory turnover ratio at the store level
    store_turnover_df = calculate_inventory_turnover_store(df)

    # Output final DataFrame
    print(df[['Date', 'Store', 'SKU', 'OrderQuantity', 'InventoryTurnover']])
    print(store_turnover_df[['Store', 'InventoryTurnover']])

    # Save final data to CSV
    output_csv = "/data/output.csv"
    
    # Remove the existing output CSV file
    if os.path.exists(output_csv):
        os.remove(output_csv)
        
    df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)

    store_turnover_csv = "/data/store_turnover.csv"
    
    # Remove the existing store turnover CSV file
    if os.path.exists(store_turnover_csv):
        os.remove(store_turnover_csv)
        
    store_turnover_df.to_csv(store_turnover_csv, mode='a', header=not os.path.exists(store_turnover_csv), index=False)


if __name__ == "__main__":
    main()
