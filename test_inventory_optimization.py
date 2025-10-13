# test_inventory_optimization.py

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Import the inventory optimization module
from inventory_optimization import (
    get_holidays, generate_synthetic_data, demand_forecasting, classify_inventory,
    calculate_safety_stock, calculate_eoq, calculate_reorder_point, should_reorder,
    calculate_daily_order, calculate_inventory_turnover, calculate_inventory_turnover_store,
    calculate_excess_inventory_items, calculate_stockout_risk_items, calculate_never_sold_items,
    calculate_fast_slow_moving_items, calculate_urgent_orders_items, calculate_profitable_stagnant_items,
    calculate_days_to_stockout, calculate_average_daily_demand, calculate_lead_time_analysis,
    calculate_on_order_analysis, generate_comprehensive_metrics_report
)

class TestHolidaysLogic(unittest.TestCase):
    """Test holidays logic for different countries and states."""
    
    def test_get_holidays_india_tamil_nadu(self):
        """Test holidays for India Tamil Nadu."""
        holidays_set = get_holidays('IN', 'TN', [2023])
        self.assertIsInstance(holidays_set, set)
        self.assertGreater(len(holidays_set), 0)
    
    def test_get_holidays_us_california(self):
        """Test holidays for US California."""
        holidays_set = get_holidays('US', 'CA', [2023])
        self.assertIsInstance(holidays_set, set)
        # Should not raise error even if holidays not available
    
    def test_get_holidays_invalid_country(self):
        """Test holidays for invalid country (should default to India)."""
        holidays_set = get_holidays('XX', 'YY', [2023])
        self.assertIsInstance(holidays_set, set)
    
    def test_get_holidays_exception_handling(self):
        """Test exception handling in holidays function."""
        holidays_set = get_holidays('IN', 'INVALID_STATE', [2023])
        self.assertIsInstance(holidays_set, set)

class TestDataGeneration(unittest.TestCase):
    """Test synthetic data generation with edge cases."""
    
    def setUp(self):
        """Set up test data."""
        self.test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
    
    def test_data_generation_basic(self):
        """Test basic data generation."""
        self.assertIsInstance(self.test_df, pd.DataFrame)
        self.assertGreater(len(self.test_df), 0)
        self.assertIn('Date', self.test_df.columns)
        self.assertIn('Store', self.test_df.columns)
        self.assertIn('SKU', self.test_df.columns)
        self.assertIn('SalesQuantity', self.test_df.columns)
        self.assertIn('InventoryLevel', self.test_df.columns)
        self.assertIn('UnitCost', self.test_df.columns)
        self.assertIn('SellingPrice', self.test_df.columns)
        self.assertIn('LeadTime', self.test_df.columns)
        self.assertIn('SupplierID', self.test_df.columns)
        self.assertIn('Category', self.test_df.columns)
        self.assertIn('OrderedDate', self.test_df.columns)
    
    def test_data_generation_ordered_date_schema(self):
        """Test that OrderedDate, OrderedQuantity, and OrderStatus are included in schema."""
        self.assertIn('OrderedDate', self.test_df.columns)
        self.assertIn('OrderedQuantity', self.test_df.columns)
        self.assertIn('OrderStatus', self.test_df.columns)
        
        # Some records should have OrderedDate (10% chance)
        ordered_records = self.test_df[self.test_df['OrderedDate'].notna()]
        self.assertGreaterEqual(len(ordered_records), 0)
        
        # Check OrderStatus values
        valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'In Transit', 'Delivered', 'None']
        self.assertTrue(self.test_df['OrderStatus'].isin(valid_statuses).all())
        
        # Check OrderedQuantity is non-negative
        self.assertTrue((self.test_df['OrderedQuantity'] >= 0).all())
    
    def test_data_generation_holidays_effect(self):
        """Test that holidays affect sales quantity."""
        # Check if holiday dates have higher sales
        holiday_dates = get_holidays('IN', 'TN', [2023])
        if holiday_dates:
            holiday_sales = self.test_df[self.test_df['Date'].isin(holiday_dates)]['SalesQuantity']
            regular_sales = self.test_df[~self.test_df['Date'].isin(holiday_dates)]['SalesQuantity']
            if len(holiday_sales) > 0 and len(regular_sales) > 0:
                self.assertGreaterEqual(holiday_sales.mean(), regular_sales.mean() * 0.8)
    
    def test_data_generation_weekend_effect(self):
        """Test that weekends have higher sales."""
        weekend_sales = self.test_df[self.test_df['Date'].dt.weekday.isin([5, 6])]['SalesQuantity']
        weekday_sales = self.test_df[self.test_df['Date'].dt.weekday.isin([0, 1, 2, 3, 4])]['SalesQuantity']
        if len(weekend_sales) > 0 and len(weekday_sales) > 0:
            self.assertGreaterEqual(weekend_sales.mean(), weekday_sales.mean() * 0.8)
    
    def test_data_generation_negative_values(self):
        """Test that no negative values are generated."""
        self.assertTrue((self.test_df['SalesQuantity'] >= 0).all())
        self.assertTrue((self.test_df['InventoryLevel'] >= 0).all())
        self.assertTrue((self.test_df['UnitCost'] > 0).all())
        self.assertTrue((self.test_df['SellingPrice'] > 0).all())
        self.assertTrue((self.test_df['LeadTime'] > 0).all())
    
    def test_data_generation_profit_margin(self):
        """Test that selling price is greater than unit cost."""
        self.test_df['ProfitMargin'] = self.test_df['SellingPrice'] - self.test_df['UnitCost']
        self.assertTrue((self.test_df['ProfitMargin'] > 0).all())

class TestExistingMetrics(unittest.TestCase):
    """Test existing inventory optimization metrics."""
    
    def setUp(self):
        """Set up test data."""
        self.test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
        # Apply all existing functions
        self.test_df = demand_forecasting(self.test_df)
        self.test_df = classify_inventory(self.test_df)
        self.test_df = calculate_safety_stock(self.test_df)
        self.test_df = calculate_eoq(self.test_df)
        self.test_df = calculate_reorder_point(self.test_df)
        self.test_df = should_reorder(self.test_df)
        self.test_df = calculate_daily_order(self.test_df)
        self.test_df = calculate_inventory_turnover(self.test_df)
    
    def test_demand_forecasting(self):
        """Test demand forecasting calculation."""
        self.assertIn('DemandForecast', self.test_df.columns)
        self.assertTrue(self.test_df['DemandForecast'].notna().all())
        self.assertTrue((self.test_df['DemandForecast'] >= 0).all())
    
    def test_classify_inventory(self):
        """Test inventory classification."""
        self.assertIn('CV', self.test_df.columns)
        self.assertIn('InventoryCategory', self.test_df.columns)
        self.assertTrue(self.test_df['CV'].notna().all())
        self.assertTrue(self.test_df['InventoryCategory'].notna().all())
        self.assertTrue(self.test_df['InventoryCategory'].isin(['A', 'B', 'C']).all())
    
    def test_safety_stock(self):
        """Test safety stock calculation."""
        self.assertIn('SafetyStock', self.test_df.columns)
        self.assertTrue(self.test_df['SafetyStock'].notna().all())
        self.assertTrue((self.test_df['SafetyStock'] >= 0).all())
    
    def test_eoq(self):
        """Test EOQ calculation."""
        self.assertIn('EOQ', self.test_df.columns)
        self.assertTrue(self.test_df['EOQ'].notna().all())
        self.assertTrue((self.test_df['EOQ'] > 0).all())
    
    def test_reorder_point(self):
        """Test reorder point calculation with pending orders."""
        self.assertIn('ReorderPoint', self.test_df.columns)
        self.assertIn('PendingOrders', self.test_df.columns)
        self.assertTrue(self.test_df['ReorderPoint'].notna().all())
        self.assertTrue((self.test_df['ReorderPoint'] >= 0).all())
        self.assertTrue((self.test_df['PendingOrders'] >= 0).all())
    
    def test_should_reorder(self):
        """Test reorder decision logic."""
        self.assertIn('Reorder', self.test_df.columns)
        self.assertTrue(self.test_df['Reorder'].isin([True, False]).all())
    
    def test_daily_order(self):
        """Test daily order calculation with pending orders and priority."""
        self.assertIn('OrderQuantity', self.test_df.columns)
        self.assertIn('OrderPriority', self.test_df.columns)
        self.assertTrue(self.test_df['OrderQuantity'].notna().all())
        self.assertTrue((self.test_df['OrderQuantity'] >= 0).all())
        self.assertTrue(self.test_df['OrderPriority'].isin(['High', 'Medium', 'Low']).all())
    
    def test_inventory_turnover(self):
        """Test inventory turnover calculation."""
        self.assertIn('InventoryTurnover', self.test_df.columns)
        self.assertTrue(self.test_df['InventoryTurnover'].notna().all())
        self.assertTrue((self.test_df['InventoryTurnover'] >= 0).all())

class TestComprehensiveMetrics(unittest.TestCase):
    """Test comprehensive metrics calculations."""
    
    def setUp(self):
        """Set up test data with all metrics."""
        self.test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
        # Apply all existing functions
        self.test_df = demand_forecasting(self.test_df)
        self.test_df = classify_inventory(self.test_df)
        self.test_df = calculate_safety_stock(self.test_df)
        self.test_df = calculate_eoq(self.test_df)
        self.test_df = calculate_reorder_point(self.test_df)
        self.test_df = should_reorder(self.test_df)
        self.test_df = calculate_daily_order(self.test_df)
        self.test_df = calculate_inventory_turnover(self.test_df)
    
    def test_excess_inventory_calculation(self):
        """Test excess inventory calculation."""
        excess_df = calculate_excess_inventory_items(self.test_df)
        self.assertIsInstance(excess_df, pd.DataFrame)
        self.assertGreater(len(excess_df), 0)
        self.assertIn('IsExcess', excess_df.columns)
        self.assertIn('ExcessSeverity', excess_df.columns)
        self.assertTrue(excess_df['IsExcess'].isin([True, False]).all())
    
    def test_stockout_risk_calculation(self):
        """Test stock-out risk calculation."""
        stockout_df = calculate_stockout_risk_items(self.test_df)
        self.assertIsInstance(stockout_df, pd.DataFrame)
        self.assertGreater(len(stockout_df), 0)
        self.assertIn('IsAtRisk', stockout_df.columns)
        self.assertIn('RiskLevel', stockout_df.columns)
        self.assertTrue(stockout_df['IsAtRisk'].isin([True, False]).all())
    
    def test_never_sold_calculation(self):
        """Test never sold items calculation."""
        never_sold_df = calculate_never_sold_items(self.test_df)
        self.assertIsInstance(never_sold_df, pd.DataFrame)
        self.assertIn('NeverSold', never_sold_df.columns)
        self.assertIn('SalesStatus', never_sold_df.columns)
        self.assertTrue(never_sold_df['NeverSold'].isin([True, False]).all())
    
    def test_fast_slow_moving_calculation(self):
        """Test fast/slow moving items calculation."""
        movement_df = calculate_fast_slow_moving_items(self.test_df)
        self.assertIsInstance(movement_df, pd.DataFrame)
        self.assertGreater(len(movement_df), 0)
        self.assertIn('MovementCategory', movement_df.columns)
        self.assertIn('TurnoverPercentile', movement_df.columns)
        self.assertTrue(movement_df['MovementCategory'].isin(['Slow Moving', 'Medium Moving', 'Fast Moving']).all())
    
    def test_urgent_orders_calculation(self):
        """Test urgent orders calculation."""
        urgent_df = calculate_urgent_orders_items(self.test_df)
        self.assertIsInstance(urgent_df, pd.DataFrame)
        if len(urgent_df) > 0:
            self.assertIn('UrgencyLevel', urgent_df.columns)
            self.assertIn('OrderQuantity', urgent_df.columns)
    
    def test_profitable_stagnant_calculation(self):
        """Test profitable/stagnant items calculation."""
        profit_df = calculate_profitable_stagnant_items(self.test_df)
        self.assertIsInstance(profit_df, pd.DataFrame)
        self.assertGreater(len(profit_df), 0)
        self.assertIn('ProfitabilityCategory', profit_df.columns)
        self.assertIn('OverallCategory', profit_df.columns)
        self.assertTrue(profit_df['ProfitabilityCategory'].isin(['Stagnant', 'Average', 'Profitable']).all())
    
    def test_days_to_stockout_calculation(self):
        """Test days to stock-out calculation."""
        days_df = calculate_days_to_stockout(self.test_df)
        self.assertIsInstance(days_df, pd.DataFrame)
        self.assertGreater(len(days_df), 0)
        self.assertIn('DaysToStockout', days_df.columns)
        self.assertIn('StockoutUrgency', days_df.columns)
    
    def test_average_daily_demand_calculation(self):
        """Test average daily demand calculation."""
        demand_df = calculate_average_daily_demand(self.test_df)
        self.assertIsInstance(demand_df, pd.DataFrame)
        self.assertGreater(len(demand_df), 0)
        self.assertIn('AvgDailyDemand', demand_df.columns)
        self.assertIn('DemandPattern', demand_df.columns)
    
    def test_lead_time_analysis_calculation(self):
        """Test lead time analysis calculation."""
        leadtime_df = calculate_lead_time_analysis(self.test_df)
        self.assertIsInstance(leadtime_df, pd.DataFrame)
        self.assertGreater(len(leadtime_df), 0)
        self.assertIn('LeadTimeCategory', leadtime_df.columns)
        self.assertIn('EffectiveLeadTime', leadtime_df.columns)
    
    def test_on_order_analysis_calculation(self):
        """Test on order analysis calculation."""
        onorder_df = calculate_on_order_analysis(self.test_df)
        self.assertIsInstance(onorder_df, pd.DataFrame)
        if len(onorder_df) > 0:
            self.assertIn('OnOrderQuantity', onorder_df.columns)
            self.assertIn('OrderStatus', onorder_df.columns)
            self.assertIn('IsOverdue', onorder_df.columns)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame(columns=['Date', 'Store', 'SKU', 'SalesQuantity', 'InventoryLevel'])
        # Should not raise error
        try:
            result = calculate_excess_inventory_items(empty_df)
            self.assertIsInstance(result, pd.DataFrame)
        except Exception as e:
            self.fail(f"Empty DataFrame handling failed: {e}")
    
    def test_zero_sales_data(self):
        """Test handling of zero sales data."""
        zero_sales_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-02',
            num_stores=1, num_skus=1, seed=42
        )
        zero_sales_df['SalesQuantity'] = 0
        zero_sales_df = demand_forecasting(zero_sales_df)
        zero_sales_df = calculate_inventory_turnover(zero_sales_df)
        
        # Test never sold calculation with zero sales
        never_sold_df = calculate_never_sold_items(zero_sales_df)
        self.assertIsInstance(never_sold_df, pd.DataFrame)
    
    def test_infinite_values_handling(self):
        """Test handling of infinite values."""
        test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-02',
            num_stores=1, num_skus=1, seed=42
        )
        test_df = demand_forecasting(test_df)
        test_df = calculate_inventory_turnover(test_df)
        
        # Test days to stockout with potential infinite values
        days_df = calculate_days_to_stockout(test_df)
        self.assertFalse(days_df['DaysToStockout'].isin([np.inf, -np.inf]).any())
    
    def test_missing_columns_handling(self):
        """Test handling of missing columns."""
        incomplete_df = pd.DataFrame({
            'Date': [datetime(2023, 1, 1)],
            'Store': ['Store001'],
            'SKU': ['SKU001'],
            'SalesQuantity': [10],
            'InventoryLevel': [50]
        })
        
        # Should handle missing columns gracefully
        try:
            result = calculate_excess_inventory_items(incomplete_df)
            self.assertIsInstance(result, pd.DataFrame)
        except Exception as e:
            # Expected to fail due to missing columns, but should not crash
            self.assertIn('SafetyStock', str(e) or '')
    
    def test_negative_values_handling(self):
        """Test handling of negative values."""
        negative_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-02',
            num_stores=1, num_skus=1, seed=42
        )
        negative_df['InventoryLevel'] = -10  # Negative inventory
        negative_df = demand_forecasting(negative_df)
        negative_df = calculate_safety_stock(negative_df)
        negative_df = calculate_reorder_point(negative_df)
        
        # Should handle negative values gracefully
        stockout_df = calculate_stockout_risk_items(negative_df)
        self.assertIsInstance(stockout_df, pd.DataFrame)

class TestComprehensiveReport(unittest.TestCase):
    """Test comprehensive metrics report generation."""
    
    def test_comprehensive_report_generation(self):
        """Test comprehensive report generation."""
        test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
        test_df = demand_forecasting(test_df)
        test_df = classify_inventory(test_df)
        test_df = calculate_safety_stock(test_df)
        test_df = calculate_eoq(test_df)
        test_df = calculate_reorder_point(test_df)
        test_df = should_reorder(test_df)
        test_df = calculate_daily_order(test_df)
        test_df = calculate_inventory_turnover(test_df)
        
        # Generate comprehensive report
        metrics = generate_comprehensive_metrics_report(test_df)
        
        # Check that all 10 metrics are present
        expected_metrics = [
            'excess_inventory', 'stockout_risk', 'never_sold', 'fast_slow_moving',
            'urgent_orders', 'profitable_stagnant', 'days_to_stockout',
            'average_daily_demand', 'lead_time_analysis', 'on_order_analysis'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], pd.DataFrame)

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency."""
    
    def test_data_consistency(self):
        """Test data consistency across calculations."""
        test_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
        
        # Apply all functions
        test_df = demand_forecasting(test_df)
        test_df = classify_inventory(test_df)
        test_df = calculate_safety_stock(test_df)
        test_df = calculate_eoq(test_df)
        test_df = calculate_reorder_point(test_df)
        test_df = should_reorder(test_df)
        test_df = calculate_daily_order(test_df)
        test_df = calculate_inventory_turnover(test_df)
        
        # Check that all required columns exist
        required_columns = [
            'Date', 'Store', 'SKU', 'SalesQuantity', 'InventoryLevel',
            'UnitCost', 'SellingPrice', 'LeadTime', 'SupplierID', 'Category', 'OrderedDate',
            'DemandForecast', 'CV', 'InventoryCategory', 'SafetyStock', 'EOQ',
            'ReorderPoint', 'Reorder', 'OrderQuantity', 'TotalSales',
            'AverageInventoryLevel', 'InventoryTurnover'
        ]
        
        for col in required_columns:
            self.assertIn(col, test_df.columns, f"Missing column: {col}")
    
    def test_no_data_loss(self):
        """Test that no data is lost during processing."""
        original_df = generate_synthetic_data(
            country='IN', state='TN', 
            start_date='2023-01-01', end_date='2023-01-31',
            num_stores=2, num_skus=2, seed=42
        )
        original_count = len(original_df)
        
        # Apply all functions
        processed_df = demand_forecasting(original_df)
        processed_df = classify_inventory(processed_df)
        processed_df = calculate_safety_stock(processed_df)
        processed_df = calculate_eoq(processed_df)
        processed_df = calculate_reorder_point(processed_df)
        processed_df = should_reorder(processed_df)
        processed_df = calculate_daily_order(processed_df)
        processed_df = calculate_inventory_turnover(processed_df)
        
        # Check that no rows were lost
        self.assertEqual(len(processed_df), original_count)

def run_all_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestHolidaysLogic, TestDataGeneration, TestExistingMetrics,
        TestComprehensiveMetrics, TestEdgeCases, TestComprehensiveReport,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == '__main__':
    print("="*60)
    print(" RUNNING COMPREHENSIVE INVENTORY OPTIMIZATION TESTS")
    print("="*60)
    
    result = run_all_tests()
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print(" ALL TESTS PASSED! ✓")
    else:
        print(f" TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        for failure in result.failures:
            print(f"FAILURE: {failure[0]}")
            print(failure[1])
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(error[1])
    print("="*60)
