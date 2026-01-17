# CSV File Format Guide

This guide explains what each CSV file means and the exact format required.

## What is "GL/P&L"?

**GL** = **General Ledger** - Your company's accounting records showing all financial transactions

**P&L** = **Profit & Loss** (also called Income Statement) - A financial report showing:
- **Revenue** (money coming in)
- **Costs** (money going out)
- **Profit/Loss** (revenue minus costs)

**gl_pnl_monthly.csv** = Monthly profit and loss data from your general ledger/accounting system

This file contains your company's monthly financial performance, which is essential for analyzing profitability and identifying improvement opportunities.

## Required CSV Files

### 1. gl_pnl_monthly.csv (REQUIRED)

**What it contains**: Monthly revenue, costs, and operating expenses

**Required Columns** (exact column names matter):
- `month` - Format: `YYYY-MM` (e.g., "2023-01", "2024-03")
- `revenue` - Total monthly revenue (must be ≥ 0)
- `cogs` - Cost of Goods Sold (must be ≥ 0)

**Optional Columns** (can be omitted or set to 0):
- `opex_sales_marketing` - Sales & Marketing operating expenses
- `opex_rnd` - Research & Development operating expenses
- `opex_gna` - General & Administrative operating expenses
- `opex_other` - Other operating expenses

**Example**:
```csv
month,revenue,cogs,opex_sales_marketing,opex_rnd,opex_gna,opex_other
2023-01,2500000,750000,400000,600000,300000,200000
2023-02,2550000,765000,410000,610000,305000,205000
2023-03,2600000,780000,420000,620000,310000,210000
```

**Notes**:
- Month must be in `YYYY-MM` format (e.g., "2023-01" not "Jan 2023" or "01/2023")
- All dollar amounts are numeric values (no currency symbols or commas)
- Values must be ≥ 0 (cannot be negative)
- At least `month`, `revenue`, and `cogs` are required
- Other opex columns default to 0 if missing

**What the system calculates from this**:
- Gross Margin = revenue - cogs
- Gross Margin % = (gross margin / revenue) × 100
- Total OpEx = sum of all opex columns
- EBITDA = gross margin - total opex
- EBITDA Margin % = (EBITDA / revenue) × 100

---

## Optional CSV Files

### 2. payroll_summary.csv (OPTIONAL)

**What it contains**: Monthly headcount and payroll costs by department/function

**Required Columns**:
- `month` - Format: `YYYY-MM`
- `function` - Must be one of: `Sales`, `Marketing`, `R&D`, `G&A`, `Ops`
- `headcount` - Number of employees (integer, must be ≥ 0)

**Optional Columns**:
- `fully_loaded_cost` - Total payroll cost including benefits, taxes (can be null/empty)

**Example**:
```csv
month,function,headcount,fully_loaded_cost
2023-01,Sales,25,187500
2023-01,Marketing,15,135000
2023-01,R&D,40,360000
2023-01,G&A,10,90000
2023-01,Ops,5,45000
2023-02,Sales,26,195000
2023-02,Marketing,15,135000
```

**Notes**:
- Multiple rows per month (one row per function)
- Function names are case-sensitive: `Sales`, `Marketing`, `R&D`, `G&A`, `Ops`
- `fully_loaded_cost` can be empty/null if not available
- Enables headcount optimization initiatives

---

### 3. vendor_spend.csv (OPTIONAL)

**What it contains**: Monthly spending by vendor and category

**Required Columns**:
- `month` - Format: `YYYY-MM`
- `vendor` - Vendor name (e.g., "AWS", "Salesforce", "Office365")
- `category` - Spending category (e.g., "Cloud Infrastructure", "CRM Software", "Communication")
- `amount` - Monthly spend amount (must be ≥ 0)

**Example**:
```csv
month,vendor,category,amount
2023-01,AWS,Cloud Infrastructure,85000
2023-01,Salesforce,CRM Software,45000
2023-01,Slack,Communication,12000
2023-01,Zendesk,Customer Support,18000
2023-02,AWS,Cloud Infrastructure,87000
2023-02,Salesforce,CRM Software,45000
```

**Notes**:
- Multiple rows per month (one row per vendor/category)
- Vendor and category are free text (you choose the names)
- Enables vendor consolidation and SaaS optimization initiatives

---

### 4. revenue_by_segment.csv (OPTIONAL)

**What it contains**: Monthly revenue broken down by customer segment

**Required Columns**:
- `month` - Format: `YYYY-MM`
- `segment` - Customer segment name (e.g., "Enterprise", "Mid-Market", "SMB", "Consumer")
- `revenue` - Revenue from this segment (must be ≥ 0)

**Example**:
```csv
month,segment,revenue
2023-01,Enterprise,1500000
2023-01,Mid-Market,750000
2023-01,SMB,250000
2023-02,Enterprise,1530000
2023-02,Mid-Market,765000
2023-02,SMB,255000
```

**Notes**:
- Multiple rows per month (one row per segment)
- Segment names are free text (you define them)
- Segment revenue should sum to total revenue in gl_pnl_monthly.csv (not required, but helpful)
- Enables segment-specific analysis

---

## Format Requirements Summary

### Common Rules for All Files

1. **File Format**: Standard CSV (comma-separated values)
2. **Header Row**: First row must contain column names (exact spelling matters)
3. **Month Format**: Must be `YYYY-MM` format
   - ✅ Valid: `2023-01`, `2024-12`, `2023-06`
   - ❌ Invalid: `Jan-2023`, `01/2023`, `2023-1`, `January 2023`
4. **Numeric Values**: 
   - No currency symbols ($, €, £)
   - No thousands separators (commas)
   - ✅ Valid: `2500000`, `1000.50`, `0`
   - ❌ Invalid: `$2,500,000`, `1,000.50`
5. **Encoding**: UTF-8 (standard)
6. **Line Endings**: Unix (LF) or Windows (CRLF) - both work

### Validation

The system validates each file when you upload:
- ✅ Checks column names match exactly
- ✅ Validates month format
- ✅ Ensures numeric values are valid
- ✅ Shows errors if format is wrong
- ✅ Only accepts valid data into the system

---

## Sample Data

Example CSV files are provided in the `sample_data/` directory. Use these as templates:

- `sample_data/gl_pnl_monthly.csv` - 24 months of sample P&L data
- `sample_data/payroll_summary.csv` - Sample payroll data
- `sample_data/vendor_spend.csv` - Sample vendor spending data
- `sample_data/revenue_by_segment.csv` - Sample segmented revenue data

---

## Common Format Issues & Fixes

### Issue: "Month must be in YYYY-MM format"
**Fix**: Change `Jan 2023` → `2023-01` or `01/2023` → `2023-01`

### Issue: "Missing required columns"
**Fix**: Check column names match exactly (case-sensitive):
- ✅ `month` (not `Month` or `MONTH`)
- ✅ `revenue` (not `Revenue` or `revenues`)
- ✅ `cogs` (not `COGS` or `cost_of_goods`)

### Issue: "Invalid numeric value"
**Fix**: Remove currency symbols and commas:
- `$2,500,000` → `2500000`
- `$1,000.50` → `1000.50`

### Issue: "Negative value not allowed"
**Fix**: Check if values should be negative (the system assumes all values ≥ 0)

### Issue: "Function must be one of..."
**Fix**: Use exact function names: `Sales`, `Marketing`, `R&D`, `G&A`, `Ops`
- Not `sales` (lowercase)
- Not `Research & Development` (full name)
- Not `General and Administrative` (full name)

---

## Exporting from Your Accounting System

### From QuickBooks/Xero/Sage:
1. Go to Reports → Profit & Loss (by month)
2. Export to CSV
3. Map columns to required format:
   - Total Income → `revenue`
   - Cost of Sales → `cogs`
   - Sales & Marketing expenses → `opex_sales_marketing`
   - R&D expenses → `opex_rnd`
   - General & Administrative → `opex_gna`
   - Other expenses → `opex_other`

### From Excel/Google Sheets:
1. Create columns: `month`, `revenue`, `cogs`, etc.
2. Format month column as `YYYY-MM` text
3. Export as CSV

---

## Minimum Viable Data

**To run the pipeline, you only need:**
- ✅ `gl_pnl_monthly.csv` with `month`, `revenue`, `cogs` columns
- ✅ At least 3 months of data (more is better)

**All other files are optional** but improve analysis quality:
- More months = better trend analysis
- Payroll data = enables headcount initiatives
- Vendor data = enables vendor consolidation initiatives
- Segment data = enables segment-specific analysis

---

## Getting Help

If you have format issues:
1. Check the error message when uploading - it tells you exactly what's wrong
2. Compare your file to the sample data in `sample_data/`
3. Use Excel/Google Sheets to verify:
   - Column names match exactly
   - Month format is `YYYY-MM`
   - Numeric values have no symbols or commas
4. Re-export from your accounting system if needed
