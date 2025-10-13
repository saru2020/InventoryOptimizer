
---

# Inventory Optimization Tool

This project provides an inventory optimization tool that uses synthetic data and applies demand forecasting, inventory classification, safety stock calculation, and other inventory management techniques. It is containerized using Docker to ensure easy deployment and portability.


## Blog

[a detailed write up](https://saru2020.medium.com/optimizing-inventory-management-with-the-inventory-optimizer-tool-5bbb431ebd12) to understand the tool in-depth.

## Requirements

Before you start, ensure you have the following installed:

- Docker: [Get Docker](https://docs.docker.com/get-docker/)

## How to Run

### Step 1: Clone the Repository

Clone the project to your local machine.

```bash
git clone https://github.com/saru2020/InventoryOptimizer.git
cd InventoryOptimizer
```

### Step 2: Add Data Directory

Make sure to have a `/data` folder at the root of the project to store input and output CSV files.

```bash
mkdir data
```

### Step 3: Build and Run the Docker Container

Use the provided `run.sh` script to build and run the Docker container. This will automatically build the image, start the container, and map the `/data` folder for storing input and output files.

```bash
chmod +x run.sh
./run.sh
```

Alternatively, you can manually run the commands:

```bash
# Build Docker image
docker build -t inventory_optimizer .

# Run Docker container
docker run -v $(pwd)/data:/data --name inventory_optimizer inventory_optimizer
```

The container will generate synthetic data and save the results to the `/data/output.csv` and `/data/store_turnover.csv` files.

### Step 4: View Results

Once the container has finished processing, the results will be stored in the `/data` folder. The main outputs are:

- **`output.csv`**: Contains the daily inventory orders, forecast data, and other information for each SKU and store.
- **`store_turnover.csv`**: Contains inventory turnover ratios for each store.

## Comprehensive Inventory Metrics

This enhanced version now supports **ALL 16 comprehensive inventory metrics**:

> 📖 **For detailed explanations, formulas, and implementation details of all metrics, see [METRICS_DOCUMENTATION.md](METRICS_DOCUMENTATION.md)**

### Core Inventory Optimization Metrics (6)

1. **Safety Stock** 🛡️ - Buffer inventory to prevent stock-outs
2. **Economic Order Quantity (EOQ)** 📦 - Optimal order quantity for cost optimization  
3. **Reorder Point** 🔄 - Inventory level for timely reordering (with pending orders)
4. **Daily Order Quantity** 📋 - Daily ordering decisions with priority ranking
5. **Inventory Turnover** 🔄 - Efficiency measurement per SKU
6. **Store Turnover** 🏪 - Store-level efficiency comparison

### Advanced Analytics Metrics (10)

7. **Excess Inventory Items** 📦 - Overstocked items identification
8. **Stock-out Risk Items** ⚠️ - Items at risk of running out
9. **Never Sold Items** 🚫 - Dead stock identification
10. **Fast/Slow Moving Items** 🏃‍♂️ - Velocity-based classification
11. **Most Urgent Orders Items** 🚨 - Priority ranking for reorders
12. **Most Profitable/Stagnant Items** 💰 - Value-based focus
13. **Days Left for Stock-out** ⏰ - Time-based urgency
14. **Average Daily Demand** 📊 - Demand baseline for forecasting
15. **Lead Time Analysis** ⏱️ - Supplier performance tracking
16. **On Order Analysis** 📋 - Pending order tracking

## Metrics Summary

| # | Metric | Category | Formula | Business Impact |
|---|--------|----------|---------|-----------------|
| 1 | Safety Stock | Core | Z-score × √(Lead Time) × Std Dev | Prevents stock-outs |
| 2 | EOQ | Core | √(2 × Demand × Order Cost / Holding Cost) | Cost optimization |
| 3 | Reorder Point | Core | Safety Stock + (Demand × Lead Time) - Pending | Timely reordering |
| 4 | Daily Order | Core | max(Reorder Point - Inventory - Pending, 0) | Daily decisions |
| 5 | Inventory Turnover | Core | Total Sales / Average Inventory | Efficiency measure |
| 6 | Store Turnover | Core | Total Sales / Average Inventory Value | Store comparison |
| 7 | Excess Inventory | Analytics | Current - (Safety + Demand × Lead Time) | Capital optimization |
| 8 | Stock-out Risk | Analytics | (Safety + Demand × Lead Time) - Current | Prevents lost sales |
| 9 | Never Sold | Analytics | Total Sales = 0 | Dead stock identification |
| 10 | Fast/Slow Moving | Analytics | Inventory Turnover classification | Velocity optimization |
| 11 | Urgent Orders | Analytics | (Reorder Point - Current) / Demand | Priority ranking |
| 12 | Profitable/Stagnant | Analytics | Profit per Unit × Total Sales | Value focus |
| 13 | Days to Stock-out | Analytics | Current Inventory / Daily Demand | Time urgency |
| 14 | Average Daily Demand | Analytics | Total Sales / Period Days | Demand baseline |
| 15 | Lead Time Analysis | Analytics | Order placement to receipt time | Supplier performance |
| 16 | On Order Analysis | Analytics | Sum of pending order quantities | Order tracking |

## Example Data

### Enhanced Input Schema

The enhanced script generates comprehensive synthetic data with all required fields:

| Date       | Store    | SKU    | SalesQuantity | InventoryLevel | UnitCost | SellingPrice | LeadTime | SupplierID | Category | OrderedDate | OrderedQuantity | OrderStatus |
|------------|----------|--------|---------------|----------------|----------|--------------|----------|------------|----------|-------------|----------------|-------------|
| 2023-01-01 | Store001 | SKU001 | 10            | 55             | 45.50    | 89.99        | 7        | SUP001     | Electronics | 2022-12-25 | 50 | Shipped |
| 2023-01-01 | Store001 | SKU002 | 14            | 42             | 25.00    | 49.99        | 5        | SUP002     | Clothing | 2022-12-28 | 30 | Confirmed |
| 2023-01-01 | Store001 | SKU003 | 9             | 75             | 15.00    | 29.99        | 3        | SUP003     | Books | null | 0 | None |

### Enhanced Output Schema

After processing, the tool outputs comprehensive inventory data with all metrics:

| Date       | Store    | SKU    | OrderQuantity | InventoryTurnover | DemandForecast | SafetyStock | ReorderPoint | Reorder | PendingOrders | OrderPriority | ExcessInventory | StockoutRisk | DaysToStockout |
|------------|----------|--------|---------------|-------------------|----------------|-------------|--------------|---------|---------------|---------------|-----------------|--------------|-----------------|
| 2023-01-01 | Store001 | SKU001 | 8             | 2.5               | 10.2          | 8.5         | 28.5         | True    | 50            | High          | -23.5           | -23.5        | 5.4            |
| 2023-01-01 | Store001 | SKU002 | 15            | 1.8               | 14.1          | 9.2         | 39.7         | False   | 30            | Medium         | -37.7           | 37.7         | 3.0            |
| 2023-01-01 | Store001 | SKU003 | 0             | 0.9               | 8.7           | 7.8         | 32.1         | False   | 0             | Low            | 42.9            | 32.1         | 8.6            |

### Store Turnover Output

| Store    | InventoryTurnover |
|----------|-------------------|
| Store001 | 2.0               |
| Store002 | 1.7               |
| Store003 | 1.5               |

### Comprehensive Metrics Output

The tool now generates **13 separate CSV files** for detailed analysis:

**Core Output Files:**
1. **`output.csv`** - Main output with all calculated metrics
2. **`source.csv`** - Enhanced input data with all required fields
3. **`store_turnover.csv`** - Store-level inventory turnover ratios

**Advanced Analytics Files:**
4. **`excess_inventory_analysis.csv`** - Excess inventory analysis
5. **`stockout_risk_analysis.csv`** - Stock-out risk analysis  
6. **`never_sold_analysis.csv`** - Never sold items analysis
7. **`fast_slow_moving_analysis.csv`** - Movement classification
8. **`urgent_orders_analysis.csv`** - Urgent orders analysis
9. **`profitable_stagnant_analysis.csv`** - Profitability analysis
10. **`days_to_stockout_analysis.csv`** - Days to stock-out analysis
11. **`average_daily_demand_analysis.csv`** - Demand analysis
12. **`lead_time_analysis_analysis.csv`** - Lead time analysis
13. **`on_order_analysis_analysis.csv`** - On order analysis

## Configuration Options

### Holiday Configuration
The system now supports configurable holidays by country and state:

```python
# Example usage with different countries/states
main(country='US', state='CA', start_date='2023-01-01', end_date='2023-12-31')
main(country='GB', state='', start_date='2023-01-01', end_date='2023-12-31')
main(country='IN', state='TN', start_date='2023-01-01', end_date='2023-12-31')
```

### Data Schema
The enhanced input schema includes all required fields for comprehensive analysis:

**Required Columns:**
- `Date`: Transaction date
- `Store`: Store identifier
- `SKU`: Product identifier
- `SalesQuantity`: Quantity sold
- `InventoryLevel`: Current inventory level
- `UnitCost`: Cost per unit
- `SellingPrice`: Selling price per unit
- `LeadTime`: Lead time in days
- `SupplierID`: Supplier identifier
- `Category`: Product category
- `OrderedDate`: Date when order was placed (for lead time calculation)
- `OrderedQuantity`: Quantity ordered (for reorder point calculation)
- `OrderStatus`: Status of the order (Pending, Confirmed, Shipped, In Transit, Delivered, None)

### Testing and Quality Assurance

The project includes comprehensive testing:

```bash
# Run all tests
python test_inventory_optimization.py

# Setup pre-commit hooks (runs tests automatically before commits)
python setup_precommit.py

# Run pre-commit on all files
pre-commit run --all-files
```

### File Outputs

- **`source.csv`**: Enhanced input data with all required fields
- **`output.csv`**: Main output with all calculated metrics
- **`store_turnover.csv`**: Store-level inventory turnover ratios
- **`*_analysis.csv`**: 10 separate files for detailed metric analysis
- **`METRICS_DOCUMENTATION.md`**: Detailed explanations of all 16 metrics

**Total: 13 CSV files + 1 documentation file** providing comprehensive inventory insights

## Advanced Usage

### Custom Data Input
To use your own data, ensure your CSV has the required schema and modify the data loading:

```python
# Load your own data
def load_custom_data(file_path):
    df = pd.read_csv(file_path)
    # Ensure all required columns exist
    required_columns = ['Date', 'Store', 'SKU', 'SalesQuantity', 'InventoryLevel', 
                       'UnitCost', 'SellingPrice', 'LeadTime', 'SupplierID', 'Category', 'OrderedDate']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return df
```

### Metric Customization
All metrics support customization:

```python
# Custom excess inventory threshold
excess_df = calculate_excess_inventory_items(df, excess_threshold=2.0)

# Custom movement classification thresholds
movement_df = calculate_fast_slow_moving_items(df)
# Modify thresholds in the function as needed
```

---

Feel free to adapt this to include more examples or additional details based on your specific project requirements!
