# oracle_to_snowflake_validation

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://img.shields.io/github/actions/workflow/status/Minshan97/oracle_to_snowflake_verification/ci.yml?branch=main)

> **Validate the data migration between Oracle and Snowflake with field-level accuracy, ensuring clean, reliable data pipelines.**

---

## Repository Structure

This repository provides scripts and procedures to:

- Extract data from Oracle
- Extract data from Snowflake tables
- Perform hash comparison and field-by-field data validation with **Pass**, **Warning**, and **Fail** labels


```
oracle_to_snowflake_verification/
│
├── oracle/
│   ├── controller.py           # Oracle control logic
│   ├── db.py                   # Oracle DB connection setup
│   ├── helper.py               # Oracle extraction & hashing utils
│   ├── queries.py              # Oracle SQL queries
│   └── services.py             # Oracle-specific services
│
├── snowflake/
│   ├── controller.py           # Snowflake control logic
│   ├── db.py                   # Snowflake DB connection setup
│   ├── helper.py               # Snowflake extraction & hashing utils
│   ├── queries.py              # Snowflake SQL queries
│   └── services.py             # Snowflake-specific services
│
├── utils/
│   └── create_snowflake_table.py # Utility to create Snowflake tables
│
├── outputs/
│   └── .gitkeep                # Placeholder to keep outputs folder tracked
│
├── sp_load_order_comment.sql   # Snowflake SP to load order comment data
├── sp_load_result_comment.sql  # Snowflake SP to load result comment data
│
├── task_order_comments.py      # Pipeline: validates ORDER_COMMENT tables
├── task_result_comments.py     # Pipeline: validates RESULT_COMMENT tables
│
└── README.md                   # Project documentation
```


---

## Validation Purpose

The scripts validate table conversions from **Oracle to Snowflake**, ensuring:

1. **Data consistency** across environments
2. Differences due to **formatting or special characters** flagged as *Warnings*
3. True value mismatches flagged as *Fails*

---

## Key Features

- **Flexible PK support** (e.g. `ORDER_PROC_ID`, `COMMENT_LINE`, `AUDIT_LINE`)
- **Hash-based quick filtering** of unchanged rows
- **Detailed field-by-field comparison** for rows with differing hashes
- **Labels each field as**:
  - **Pass** – exact match
  - **Warning** – matches after normalization (e.g. whitespace, special characters, value order)
  - **Fail** – different values
- **Exports results** to structured CSVs in `outputs/`

---

## Getting Started

### Prerequisites

- Python 3.8+
- Oracle client libraries installed and configured (if needed)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Minshan97/oracle_to_snowflake_verification.git
    cd oracle_to_snowflake_verification
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
  Note: not available now. To be updated
  
3. **Configure database credentials:**

    Update your `.env` file with Oracle and Snowflake connection details.

---

## Running the Validation

Run the validation tasks with:

```bash
python task_order_comments.py
python task_result_comments.py
```

Outputs

Each run generates:

Per-batch CSVs:
outputs/column_differences_slim_{CATEGORY}_offset_{offset}_{timestamp}.csv

Full aggregated CSV:
outputs/column_differences_slim_{CATEGORY}_ALL_{timestamp}.csv
