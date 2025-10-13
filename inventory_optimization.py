# inventory_optimization.py

import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays
import warnings
from typing import Dict, List, Tuple, Optional, Union
warnings.filterwarnings('ignore')

def get_holidays(country: str = 'IN', state: str = 'TN', years: List[int] = None) -> set:
    """
    Get holidays for a specific country and state.
    
    Args:
        country: Country code (e.g., 'IN', 'US', 'GB')
        state: State/region code (e.g., 'TN', 'CA', 'NY')
        years: List of years to get holidays for
    
    Returns:
        Set of holiday dates
    """
    if years is None:
        years = [datetime.now().year]
    
    try:
        if country == 'IN':
            holiday_dict = holidays.IN(state=state, years=years)
        elif country == 'US':
            holiday_dict = holidays.US(state=state, years=years)
        elif country == 'GB':
            holiday_dict = holidays.GB(years=years)
        else:
            # Default to India if country not supported
            holiday_dict = holidays.IN(state=state, years=years)
        
        # Convert holiday dictionary to set of dates
        return set(holiday_dict.keys())
    except Exception:
        # Return empty set if holidays not available
        return set()

def generate_synthetic_data(country: str = 'IN', state: str = 'TN', 
                          start_date: str = '2023-01-01', end_date: str = '2023-12-31',
                          num_stores: int = 3, num_skus: int = 3, seed: int = 0):
    """
    Generate comprehensive synthetic data with all required fields for inventory optimization.
    
    Args:
        country: Country code for holidays
        state: State code for holidays
        start_date: Start date for data generation
        end_date: End date for data generation
        num_stores: Number of stores to generate
        num_skus: Number of SKUs to generate
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with comprehensive inventory data
    """
    np.random.seed(seed)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    date_range = pd.date_range(start_dt, end_dt, freq='D')
    
    # Generate SKU and store lists
    sku_list = [f'SKU{i:03d}' for i in range(1, num_skus + 1)]
    store_list = [f'Store{i:03d}' for i in range(1, num_stores + 1)]
    
    # Get holidays for the specified country/state
    holiday_dates = get_holidays(country, state, [start_dt.year, end_dt.year])
    
    # Define SKU categories with different characteristics
    sku_categories = {
        'Electronics': {'base_cost': 200, 'cost_variance': 0.3, 'base_price': 300, 'demand_multiplier': 1.2, 'lead_time': 7},
        'Clothing': {'base_cost': 50, 'cost_variance': 0.4, 'base_price': 100, 'demand_multiplier': 1.0, 'lead_time': 5},
        'Books': {'base_cost': 20, 'cost_variance': 0.2, 'base_price': 35, 'demand_multiplier': 0.8, 'lead_time': 3},
        'Home': {'base_cost': 100, 'cost_variance': 0.5, 'base_price': 180, 'demand_multiplier': 0.9, 'lead_time': 10},
        'Sports': {'base_cost': 80, 'cost_variance': 0.3, 'base_price': 150, 'demand_multiplier': 1.1, 'lead_time': 14}
    }
    
    # Generate SKU master data
    sku_master = {}
    for i, sku in enumerate(sku_list):
        category = list(sku_categories.keys())[i % len(sku_categories)]
        cat_data = sku_categories[category]
        
        unit_cost = max(np.random.normal(cat_data['base_cost'], cat_data['base_cost'] * cat_data['cost_variance']), cat_data['base_cost'] * 0.5)
        selling_price = max(np.random.normal(cat_data['base_price'], cat_data['base_price'] * 0.2), unit_cost * 1.2)
        
        sku_master[sku] = {
            'Category': category,
            'UnitCost': round(unit_cost, 2),
            'SellingPrice': round(selling_price, 2),
            'LeadTime': cat_data['lead_time'],
            'DemandMultiplier': cat_data['demand_multiplier'],
            'SupplierID': f'SUP{i % 3 + 1:03d}'
        }

    data = []
    for date in date_range:
        for store in store_list:
            for sku in sku_list:
                sku_data = sku_master[sku]
                
                # Base demand calculation
                base_demand = np.random.poisson(10)
                demand = base_demand * sku_data['DemandMultiplier']
                
                # Apply holiday effect
                if date in holiday_dates:
                    demand *= 1.3
                
                # Apply day of week effect
                if date.weekday() in [5, 6]:  # Weekend
                    demand *= 1.2
                
                # Apply seasonality
                month = date.month
                if month in [11, 12, 1]:  # Holiday season
                    demand *= 1.5
                elif month in [6, 7, 8]:  # Summer
                    demand *= 1.2
                
                # Add some randomness and ensure non-negative
                sales_quantity = max(0, int(np.random.poisson(demand)))
                
                # Generate inventory level (simplified)
                inventory_level = max(0, np.random.randint(10, 100))
                
                # Generate order information (some historical orders)
                order_date = None
                ordered_quantity = 0
                order_status = 'None'
                
                if np.random.random() < 0.1:  # 10% chance of having an order
                    order_date = date - timedelta(days=np.random.randint(1, 30))
                    ordered_quantity = np.random.randint(10, 100)
                    # Generate order status based on order age
                    days_since_order = (date - order_date).days
                    if days_since_order < sku_data['LeadTime']:
                        order_status = np.random.choice(['Pending', 'Confirmed'], p=[0.3, 0.7])
                    elif days_since_order < sku_data['LeadTime'] + 3:
                        order_status = np.random.choice(['Shipped', 'In Transit'], p=[0.6, 0.4])
                    else:
                        order_status = 'Delivered'
                
                data.append([
                    date, store, sku, sales_quantity, inventory_level,
                    sku_data['UnitCost'], sku_data['SellingPrice'], sku_data['LeadTime'],
                    sku_data['SupplierID'], sku_data['Category'], order_date,
                    ordered_quantity, order_status
                ])
    
    # Create DataFrame with comprehensive columns
    df = pd.DataFrame(data, columns=[
        'Date', 'Store', 'SKU', 'SalesQuantity', 'InventoryLevel',
        'UnitCost', 'SellingPrice', 'LeadTime', 'SupplierID', 'Category', 'OrderedDate',
        'OrderedQuantity', 'OrderStatus'
    ])
    
    # Save to CSV - use appropriate path based on environment
    if os.path.exists("/data"):
        # Docker environment
        source_csv = "/data/source.csv"
        os.makedirs("/data", exist_ok=True)
    else:
        # Local environment
        source_csv = "data/source.csv"
        os.makedirs("data", exist_ok=True)
    
    if os.path.exists(source_csv):
        os.remove(source_csv)
        
    df.to_csv(source_csv, index=False)

    return df

def demand_forecasting(df):
    # Calculate rolling average demand
    df['DemandForecast'] = df.groupby(['Store', 'SKU'])['SalesQuantity'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    return df

# The classify_inventory function categorizes inventory items (SKUs) for each store based on the variability of their demand.
# It does this by:
# 1. Calculating the coefficient of variation (CV) for the sales quantity of each SKU in each store. The CV is a measure of relative variability, computed as the standard deviation divided by the mean of sales.
# 2. Using predefined thresholds (0.1 and 0.3), it classifies each SKU into one of three categories:
#    - 'A' for low variability (CV <= 0.1)
#    - 'B' for medium variability (0.1 < CV <= 0.3)
#    - 'C' for high variability (CV > 0.3)
# The function adds two new columns to the DataFrame: 'CV' (the coefficient of variation) and 'InventoryCategory' (the assigned category).
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
    """
    Calculate reorder point considering pending orders.
    
    Formula: Reorder Point = Safety Stock + (Average Daily Demand × Lead Time) - Pending Orders
    """
    # Calculate base reorder point
    df['ReorderPoint'] = df['SafetyStock'] + (df['DemandForecast'] * df['LeadTime'])
    
    # Calculate pending orders (orders that are not delivered yet)
    df['PendingOrders'] = df.apply(lambda row: 
        row['OrderedQuantity'] if row['OrderStatus'] in ['Pending', 'Confirmed', 'Shipped', 'In Transit'] 
        else 0, axis=1
    )
    
    # Adjust reorder point by subtracting pending orders
    df['ReorderPoint'] = df['ReorderPoint'] - df['PendingOrders']
    
    # Ensure reorder point is not negative
    df['ReorderPoint'] = df['ReorderPoint'].clip(lower=0)
    
    return df

def should_reorder(df):
    # Determine if the stock should be reordered
    df['Reorder'] = df['InventoryLevel'] < df['ReorderPoint']
    return df

def calculate_daily_order(df):
    """
    Calculate daily order quantities considering pending orders.
    
    Formula: Order Quantity = max(Reorder Point - Current Inventory - Pending Orders, 0)
    """
    # Calculate order quantity considering pending orders
    df['OrderQuantity'] = df.apply(lambda row: 
        max(row['ReorderPoint'] - row['InventoryLevel'] - row['PendingOrders'], 0) 
        if row['Reorder'] else 0, axis=1
    )
    
    # Add order priority based on urgency
    df['OrderPriority'] = df.apply(lambda row:
        'High' if row['OrderQuantity'] > row['DemandForecast'] * 7 else
        'Medium' if row['OrderQuantity'] > row['DemandForecast'] * 3 else
        'Low', axis=1
    )
    
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

# =============================================================================
# COMPREHENSIVE INVENTORY METRICS CALCULATIONS
# =============================================================================

def calculate_excess_inventory_items(df, excess_threshold: float = 1.5):
    """
    Calculate excess inventory items.
    
    Formula: Excess Inventory = Current Inventory - (Safety Stock + Average Daily Demand × Lead Time)
    Threshold: 1.5 × (Safety Stock + Average Daily Demand × Lead Time)
    
    Args:
        df: DataFrame with inventory data
        excess_threshold: Multiplier for excess threshold (default 1.5)
    
    Returns:
        DataFrame with excess inventory analysis
    """
    df = df.copy()
    
    # Check if required columns exist
    required_columns = ['SafetyStock', 'DemandForecast', 'LeadTime', 'InventoryLevel']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # Return empty DataFrame with expected columns if data is incomplete
        return pd.DataFrame(columns=['Date', 'Store', 'SKU', 'InventoryLevel', 'ExcessThreshold', 'ExcessInventory', 'IsExcess', 'ExcessSeverity'])
    
    if len(df) == 0:
        return pd.DataFrame(columns=['Date', 'Store', 'SKU', 'InventoryLevel', 'ExcessThreshold', 'ExcessInventory', 'IsExcess', 'ExcessSeverity'])
    
    # Calculate excess threshold
    df['ExcessThreshold'] = excess_threshold * (df['SafetyStock'] + df['DemandForecast'] * df['LeadTime'])
    df['ExcessInventory'] = df['InventoryLevel'] - df['ExcessThreshold']
    df['IsExcess'] = df['ExcessInventory'] > 0
    
    # Calculate excess severity
    if len(df) > 0:
        df['ExcessSeverity'] = pd.cut(
            df['ExcessInventory'], 
            bins=[-np.inf, 0, df['ExcessThreshold'].quantile(0.5), df['ExcessThreshold'].quantile(0.8), np.inf],
            labels=['Normal', 'Low Excess', 'Medium Excess', 'High Excess']
        )
    else:
        df['ExcessSeverity'] = pd.Series(dtype='category')
    
    return df[['Date', 'Store', 'SKU', 'InventoryLevel', 'ExcessThreshold', 'ExcessInventory', 'IsExcess', 'ExcessSeverity']]

def calculate_stockout_risk_items(df):
    """
    Calculate stock-out risk items.
    
    Formula: Stock-out Risk = (Safety Stock + Average Daily Demand × Lead Time) - Current Inventory
    Days to Stock-out = Current Inventory / Average Daily Demand
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with stock-out risk analysis
    """
    df = df.copy()
    
    # Calculate stock-out risk
    df['StockoutRisk'] = df['SafetyStock'] + (df['DemandForecast'] * df['LeadTime']) - df['InventoryLevel']
    df['IsAtRisk'] = df['StockoutRisk'] < 0
    
    # Calculate days to stock-out
    df['DaysToStockout'] = df['InventoryLevel'] / df['DemandForecast']
    df['DaysToStockout'] = df['DaysToStockout'].replace([np.inf, -np.inf], np.nan)
    
    # Categorize risk levels
    df['RiskLevel'] = pd.cut(
        df['DaysToStockout'],
        bins=[0, 3, 7, 14, np.inf],
        labels=['Critical', 'High', 'Medium', 'Low']
    )
    
    return df[['Date', 'Store', 'SKU', 'InventoryLevel', 'StockoutRisk', 'IsAtRisk', 'DaysToStockout', 'RiskLevel']]

def calculate_never_sold_items(df):
    """
    Calculate never sold items.
    
    Formula: Never Sold = Total Sales Quantity over analysis period = 0
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with never sold items analysis
    """
    # Get latest data for each SKU-store combination
    latest_data = df.groupby(['Store', 'SKU']).last().reset_index()
    
    # Identify never sold items
    never_sold = latest_data[latest_data['TotalSales'] == 0].copy()
    never_sold['NeverSold'] = True
    never_sold['SalesStatus'] = 'Never Sold'
    
    # Identify low sales items (less than 10% of average)
    avg_sales = latest_data['TotalSales'].mean()
    low_sales = latest_data[
        (latest_data['TotalSales'] > 0) & 
        (latest_data['TotalSales'] < avg_sales * 0.1)
    ].copy()
    low_sales['NeverSold'] = False
    low_sales['SalesStatus'] = 'Low Sales'
    
    # Combine results
    result = pd.concat([never_sold, low_sales], ignore_index=True)
    
    return result[['Store', 'SKU', 'TotalSales', 'NeverSold', 'SalesStatus', 'InventoryLevel']]

def calculate_fast_slow_moving_items(df):
    """
    Calculate fast/slow moving items based on inventory turnover.
    
    Formula: Inventory Turnover = Total Sales Quantity / Average Inventory Level
    Classification: Fast Moving (>2.0), Medium Moving (1.0-2.0), Slow Moving (<1.0)
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with fast/slow moving classification
    """
    # Get latest data for each SKU-store combination
    latest_data = df.groupby(['Store', 'SKU']).last().reset_index()
    
    # Classify based on inventory turnover
    latest_data['MovementCategory'] = pd.cut(
        latest_data['InventoryTurnover'],
        bins=[0, 1.0, 2.0, np.inf],
        labels=['Slow Moving', 'Medium Moving', 'Fast Moving']
    )
    
    # Add additional metrics
    latest_data['TurnoverPercentile'] = latest_data['InventoryTurnover'].rank(pct=True) * 100
    
    return latest_data[['Store', 'SKU', 'InventoryTurnover', 'MovementCategory', 'TurnoverPercentile', 'TotalSales']]

def calculate_urgent_orders_items(df):
    """
    Calculate most urgent orders items.
    
    Formula: Urgency Score = (Reorder Point - Current Inventory) / Average Daily Demand
    Most Urgent = Items where Reorder = True AND Urgency Score > 0
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with urgent orders analysis
    """
    df = df.copy()
    
    # Calculate reorder status
    df['Reorder'] = df['InventoryLevel'] < df['ReorderPoint']
    df['OrderQuantity'] = np.maximum(df['ReorderPoint'] - df['InventoryLevel'], 0)
    
    # Calculate urgency score
    df['UrgencyScore'] = (df['ReorderPoint'] - df['InventoryLevel']) / df['DemandForecast']
    df['UrgencyScore'] = df['UrgencyScore'].replace([np.inf, -np.inf], np.nan)
    
    # Categorize urgency
    df['UrgencyLevel'] = pd.cut(
        df['UrgencyScore'],
        bins=[-np.inf, 0, 3, 7, np.inf],
        labels=['Critical', 'High', 'Medium', 'Low']
    )
    
    # Filter for items that need reordering
    urgent_items = df[df['Reorder']].copy()
    
    return urgent_items[['Date', 'Store', 'SKU', 'InventoryLevel', 'ReorderPoint', 'OrderQuantity', 'UrgencyScore', 'UrgencyLevel']]

def calculate_profitable_stagnant_items(df):
    """
    Calculate most profitable and stagnant items.
    
    Formula: 
    - Profit per Unit = Selling Price - Unit Cost
    - Total Profit = Profit per Unit × Total Sales Quantity
    - Profitability Ratio = Total Profit / Total Sales Quantity
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with profitability analysis
    """
    # Get latest data for each SKU-store combination
    latest_data = df.groupby(['Store', 'SKU']).last().reset_index()
    
    # Calculate profitability metrics
    latest_data['ProfitPerUnit'] = latest_data['SellingPrice'] - latest_data['UnitCost']
    latest_data['TotalProfit'] = latest_data['SalesQuantity'] * latest_data['ProfitPerUnit']
    latest_data['ProfitabilityRatio'] = latest_data['TotalProfit'] / latest_data['TotalSales']
    
    # Calculate profitability percentiles
    latest_data['ProfitabilityPercentile'] = latest_data['ProfitabilityRatio'].rank(pct=True) * 100
    latest_data['SalesPercentile'] = latest_data['TotalSales'].rank(pct=True) * 100
    
    # Classify profitability
    latest_data['ProfitabilityCategory'] = pd.cut(
        latest_data['ProfitabilityPercentile'],
        bins=[0, 20, 80, 100],
        labels=['Stagnant', 'Average', 'Profitable']
    )
    
    # Classify sales performance
    latest_data['SalesCategory'] = pd.cut(
        latest_data['SalesPercentile'],
        bins=[0, 20, 80, 100],
        labels=['Low Sales', 'Average Sales', 'High Sales']
    )
    
    # Combined classification
    latest_data['OverallCategory'] = latest_data.apply(
        lambda row: f"{row['ProfitabilityCategory']} - {row['SalesCategory']}", axis=1
    )
    
    return latest_data[['Store', 'SKU', 'TotalSales', 'TotalProfit', 'ProfitabilityRatio', 
                      'ProfitabilityCategory', 'SalesCategory', 'OverallCategory']]

def calculate_days_to_stockout(df):
    """
    Calculate days left for stock-out.
    
    Formula: Days to Stock-out = Current Inventory Level / Average Daily Demand
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with days to stock-out analysis
    """
    df = df.copy()
    
    # Calculate days to stock-out
    df['DaysToStockout'] = df['InventoryLevel'] / df['DemandForecast']
    df['DaysToStockout'] = df['DaysToStockout'].replace([np.inf, -np.inf], np.nan)
    
    # Categorize urgency
    df['StockoutUrgency'] = pd.cut(
        df['DaysToStockout'],
        bins=[0, 3, 7, 14, np.inf],
        labels=['Critical', 'Urgent', 'Normal', 'Safe']
    )
    
    return df[['Date', 'Store', 'SKU', 'InventoryLevel', 'DemandForecast', 'DaysToStockout', 'StockoutUrgency']]

def calculate_average_daily_demand(df):
    """
    Calculate average daily demand.
    
    Formula: Average Daily Demand = Total Sales Quantity / Number of Days in Period
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with average daily demand analysis
    """
    # Calculate average daily demand by SKU-store
    demand_analysis = df.groupby(['Store', 'SKU']).agg({
        'SalesQuantity': ['mean', 'std', 'min', 'max'],
        'DemandForecast': 'mean'
    }).round(2)
    
    # Flatten column names
    demand_analysis.columns = ['AvgDailyDemand', 'DemandStd', 'MinDemand', 'MaxDemand', 'ForecastDemand']
    demand_analysis = demand_analysis.reset_index()
    
    # Calculate demand variability
    demand_analysis['DemandVariability'] = demand_analysis['DemandStd'] / demand_analysis['AvgDailyDemand']
    demand_analysis['DemandVariability'] = demand_analysis['DemandVariability'].replace([np.inf, -np.inf], np.nan)
    
    # Categorize demand patterns
    demand_analysis['DemandPattern'] = pd.cut(
        demand_analysis['DemandVariability'],
        bins=[0, 0.3, 0.7, np.inf],
        labels=['Stable', 'Moderate', 'Variable']
    )
    
    return demand_analysis

def calculate_lead_time_analysis(df):
    """
    Calculate lead time analysis.
    
    Formula: Lead Time = Time between order placement and receipt
    Effective Lead Time = Lead Time × (1 + Lead Time Variance)
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with lead time analysis
    """
    # Get unique SKU-store combinations with lead time data
    lead_time_data = df.groupby(['Store', 'SKU']).agg({
        'LeadTime': 'first',
        'SupplierID': 'first',
        'OrderedDate': 'first'
    }).reset_index()
    
    # Calculate effective lead time (including variance)
    lead_time_data['EffectiveLeadTime'] = lead_time_data['LeadTime'] * 1.1  # 10% variance
    
    # Categorize lead times
    lead_time_data['LeadTimeCategory'] = pd.cut(
        lead_time_data['LeadTime'],
        bins=[0, 7, 14, 30, np.inf],
        labels=['Short', 'Medium', 'Long', 'Very Long']
    )
    
    # Calculate days since last order
    current_date = df['Date'].max()
    lead_time_data['DaysSinceLastOrder'] = (current_date - lead_time_data['OrderedDate']).dt.days
    lead_time_data['DaysSinceLastOrder'] = lead_time_data['DaysSinceLastOrder'].fillna(999)
    
    return lead_time_data

def calculate_on_order_analysis(df):
    """
    Calculate on order analysis using OrderedQuantity and OrderStatus.
    
    Formula: On Order = Sum of all pending order quantities for the item
    
    Args:
        df: DataFrame with inventory data
    
    Returns:
        DataFrame with on order analysis
    """
    # Get current date for analysis
    current_date = df['Date'].max()
    
    # Filter orders that are still pending based on OrderStatus
    pending_orders = df[
        (df['OrderStatus'].isin(['Pending', 'Confirmed', 'Shipped', 'In Transit'])) &
        (df['OrderedQuantity'] > 0)
    ].copy()
    
    if len(pending_orders) == 0:
        # Return empty DataFrame with expected columns if no pending orders
        return pd.DataFrame(columns=['Store', 'SKU', 'OnOrderQuantity', 'OrderStatus', 'DaysSinceOrder', 'IsOverdue', 'LeadTime'])
    
    # Calculate days since order
    pending_orders['DaysSinceOrder'] = (current_date - pending_orders['OrderedDate']).dt.days
    pending_orders['DaysSinceOrder'] = pending_orders['DaysSinceOrder'].fillna(0)
    
    # Calculate expected delivery date
    pending_orders['ExpectedDelivery'] = pending_orders['OrderedDate'] + pd.to_timedelta(pending_orders['LeadTime'], unit='D')
    
    # Check if overdue
    pending_orders['IsOverdue'] = pending_orders['ExpectedDelivery'] < current_date
    
    # Aggregate by SKU-store
    on_order_summary = pending_orders.groupby(['Store', 'SKU']).agg({
        'OrderedQuantity': 'sum',  # Total quantity on order
        'OrderStatus': lambda x: ', '.join(x.unique()),  # All order statuses
        'DaysSinceOrder': 'mean',
        'IsOverdue': 'any',
        'LeadTime': 'first'
    }).reset_index()
    
    on_order_summary.columns = ['Store', 'SKU', 'OnOrderQuantity', 'OrderStatus', 'DaysSinceOrder', 'IsOverdue', 'LeadTime']
    
    return on_order_summary

def generate_comprehensive_metrics_report(df):
    """
    Generate comprehensive metrics report with all 10 requested metrics.
    
    Args:
        df: DataFrame with processed inventory data
    
    Returns:
        Dictionary containing all metrics analysis
    """
    print("Generating comprehensive inventory metrics report...")
    
    # Calculate all metrics
    metrics = {
        'excess_inventory': calculate_excess_inventory_items(df),
        'stockout_risk': calculate_stockout_risk_items(df),
        'never_sold': calculate_never_sold_items(df),
        'fast_slow_moving': calculate_fast_slow_moving_items(df),
        'urgent_orders': calculate_urgent_orders_items(df),
        'profitable_stagnant': calculate_profitable_stagnant_items(df),
        'days_to_stockout': calculate_days_to_stockout(df),
        'average_daily_demand': calculate_average_daily_demand(df),
        'lead_time_analysis': calculate_lead_time_analysis(df),
        'on_order_analysis': calculate_on_order_analysis(df)
    }
    
    return metrics

def save_metrics_to_csv(metrics, output_dir="data"):
    """Save all metrics to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for metric_name, df in metrics.items():
        filename = f"{output_dir}/{metric_name}_analysis.csv"
        df.to_csv(filename, index=False)
        print(f"✓ Saved {metric_name} analysis to {filename}")

def print_metrics_summary(metrics):
    """Print summary of all calculated metrics."""
    print("\n" + "="*60)
    print(" COMPREHENSIVE INVENTORY METRICS SUMMARY")
    print("="*60)
    
    for metric_name, df in metrics.items():
        print(f"\n{metric_name.upper().replace('_', ' ')}:")
        print(f"  - Records: {len(df)}")
        if len(df) > 0:
            print(f"  - Columns: {list(df.columns)}")
            if 'IsExcess' in df.columns:
                excess_count = len(df[df['IsExcess'] == True])
                print(f"  - Items with excess inventory: {excess_count}")
            if 'IsAtRisk' in df.columns:
                risk_count = len(df[df['IsAtRisk'] == True])
                print(f"  - Items at stock-out risk: {risk_count}")
            if 'NeverSold' in df.columns:
                never_sold_count = len(df[df['NeverSold'] == True])
                print(f"  - Never sold items: {never_sold_count}")

def main(country='IN', state='TN', start_date='2023-01-01', end_date='2023-12-31', 
         num_stores=3, num_skus=3, seed=0):
    """
    Main function to run comprehensive inventory optimization with all metrics.
    
    Args:
        country: Country code for holidays (default: 'IN')
        state: State code for holidays (default: 'TN')
        start_date: Start date for analysis (default: '2023-01-01')
        end_date: End date for analysis (default: '2023-12-31')
        num_stores: Number of stores (default: 3)
        num_skus: Number of SKUs (default: 3)
        seed: Random seed (default: 0)
    """
    print("="*60)
    print(" COMPREHENSIVE INVENTORY OPTIMIZATION TOOL")
    print("="*60)
    print(f"Country: {country}, State: {state}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Stores: {num_stores}, SKUs: {num_skus}")
    print("="*60)
    
    # Step 1: Generate synthetic data with configurable holidays
    print("\nStep 1: Generating synthetic data...")
    df = generate_synthetic_data(country, state, start_date, end_date, num_stores, num_skus, seed)
    print(f"✓ Generated {len(df)} records")

    # Step 2: Apply existing inventory optimization functions
    print("\nStep 2: Applying inventory optimization...")
    df = demand_forecasting(df)
    df = classify_inventory(df)
    df = calculate_safety_stock(df)
    df = calculate_eoq(df)
    df = calculate_reorder_point(df)
    df = should_reorder(df)
    df = calculate_daily_order(df)
    df = calculate_inventory_turnover(df)
    store_turnover_df = calculate_inventory_turnover_store(df)
    print("✓ Applied all existing optimization functions")

    # Step 3: Calculate comprehensive metrics
    print("\nStep 3: Calculating comprehensive metrics...")
    metrics = generate_comprehensive_metrics_report(df)
    print("✓ Calculated all 10 comprehensive metrics")

    # Step 4: Save all results
    print("\nStep 4: Saving results...")
    
    # Determine output directory based on environment
    if os.path.exists("/data"):
        # Docker environment
        output_dir = "/data"
    else:
        # Local environment
        output_dir = "data"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main output
    output_csv = f"{output_dir}/output.csv"
    if os.path.exists(output_csv):
        os.remove(output_csv)
    df.to_csv(output_csv, index=False)
    print(f"✓ Saved main output to {output_csv}")
    
    # Save store turnover
    store_turnover_csv = f"{output_dir}/store_turnover.csv"
    if os.path.exists(store_turnover_csv):
        os.remove(store_turnover_csv)
    store_turnover_df.to_csv(store_turnover_csv, index=False)
    print(f"✓ Saved store turnover to {store_turnover_csv}")
    
    # Save all metrics
    save_metrics_to_csv(metrics, output_dir)
    
    # Step 5: Display summary
    print_metrics_summary(metrics)
    
    print("\n" + "="*60)
    print(" ANALYSIS COMPLETE!")
    print("="*60)
    print("All metrics have been calculated and saved to the 'data' directory.")
    print("Check the individual CSV files for detailed analysis of each metric.")


if __name__ == "__main__":
    main()
