
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

## Example Data

### Input

The script generates synthetic data that simulates store-level sales and inventory information. Below is a sample of what the synthetic data ([`source.csv`](https://github.com/saru2020/InventoryOptimizer/blob/main/data/source.csv)) might look like:

| Date       | Store    | SKU    | SalesQuantity | InventoryLevel |
|------------|----------|--------|---------------|----------------|
| 2023-01-01 | Store001 | SKU001 | 10            | 55             |
| 2023-01-01 | Store001 | SKU002 | 14            | 42             |
| 2023-01-01 | Store001 | SKU003 | 9             | 75             |
| 2023-01-02 | Store001 | SKU001 | 7             | 68             |
| 2023-01-02 | Store001 | SKU002 | 15            | 34             |

### Output

After processing, the tool will output optimized inventory data. Here is a sample from the [`output.csv`](https://github.com/saru2020/InventoryOptimizer/blob/main/data/output.csv) file:

| Date       | Store    | SKU    | OrderQuantity | InventoryTurnover |
|------------|----------|--------|---------------|-------------------|
| 2023-01-01 | Store001 | SKU001 | 12            | 2.5               |
| 2023-01-01 | Store001 | SKU002 | 5             | 1.8               |
| 2023-01-01 | Store001 | SKU003 | 0             | 0.9               |

And a sample from the [`store_turnover.csv`](https://github.com/saru2020/InventoryOptimizer/blob/main/data/store_turnover.csv) file:

| Store    | InventoryTurnover |
|----------|-------------------|
| Store001 | 2.0               |
| Store002 | 1.7               |
| Store003 | 1.5               |

### Configuration

- **`source.csv`**: The input file is generated during execution with synthetic data based on Tamil Nadu holidays.
- **`output.csv`**: Contains optimized daily order quantities and other calculated metrics like demand forecast and reorder points.
- **`store_turnover.csv`**: Contains the inventory turnover ratios at the store level.

## Additional Configuration

- The Python script generates synthetic data by default, but you can replace the `generate_synthetic_data` function to load real data from a CSV file.
- Modify the Dockerfile to install additional dependencies or adjust project settings.

---

Feel free to adapt this to include more examples or additional details based on your specific project requirements!
