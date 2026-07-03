"""
utils.py
--------
Helper functions used across the Payslip Generator project:
- Loading employee data from CSV/Excel
- Calculating Net Pay
- Saving processed data
- Small path/validation helpers

Keeping these in one place makes main.py easier to read and keeps
the "business logic" (salary formula) in a single, testable spot.
"""

import os
import re
import pandas as pd


# Columns that MUST be present in the input file for the project to work.
REQUIRED_COLUMNS = [
    "Employee_ID",
    "Employee_Name",
    "Department",
    "Designation",
    "Basic_Salary",
    "HRA",
    "DA",
    "Other_Allowance",
    "Bonus",
    "Tax_Percentage",
    "PF_Percentage",
]

# Numeric columns used in the Net Pay calculation.
NUMERIC_COLUMNS = [
    "Basic_Salary", "HRA", "DA", "Other_Allowance",
    "Bonus", "Tax_Percentage", "PF_Percentage",
]

# The dataset has no Email column, so generated emails use this domain.
# Change this to your real company domain if you have one.
COMPANY_EMAIL_DOMAIN = "novatechcorp.com"


def ensure_dir(path: str) -> None:
    """Create a directory (and any missing parent folders) if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def _generate_email(name: str, employee_id: str) -> str:
    """
    Build a placeholder email address from an employee's name, e.g.
    "Sanjay Verma" -> "sanjay.verma@novatechcorp.com".
    Falls back to the Employee_ID if the name is unusable.
    """
    if not isinstance(name, str) or not name.strip():
        return f"{str(employee_id).lower()}@{COMPANY_EMAIL_DOMAIN}"

    slug = re.sub(r"[^a-z\s]", "", name.lower()).strip()
    slug = ".".join(slug.split())
    if not slug:
        slug = str(employee_id).lower()
    return f"{slug}@{COMPANY_EMAIL_DOMAIN}"


def load_employee_data(file_path: str) -> pd.DataFrame:
    """
    Load employee data from either a .csv or .xlsx file.

    If the file has no "Email" column, one is generated automatically
    from each employee's name (see _generate_email) so the rest of the
    pipeline — PDF generation and emailing — still works. Replace the
    generated addresses with real ones whenever you have them.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file type is unsupported or required columns are missing.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type '{ext}'. Use .csv or .xlsx.")

    # Validate that all required columns exist before we go any further.
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Input file is missing required columns: {missing_cols}")

    # Auto-generate an Email column if the dataset doesn't have one.
    if "Email" not in df.columns:
        df["Email"] = [
            _generate_email(name, emp_id)
            for name, emp_id in zip(df["Employee_Name"], df["Employee_ID"])
        ]

    return df


def calculate_net_pay(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Net Pay for every employee and add it as a new column.

    Formula:
        Gross Earnings = Basic_Salary + HRA + DA + Other_Allowance + Bonus
        PF Deduction   = Basic_Salary * PF_Percentage / 100
        Tax Deduction  = Gross Earnings * Tax_Percentage / 100
        Net Pay        = Gross Earnings - PF Deduction - Tax Deduction

    Also computes Gross_Earnings, PF_Amount, and Tax_Amount as helper
    columns so the PDF generator doesn't need to redo this math.
    """
    df = df.copy()

    # Basic sanity check: numeric columns should actually be numeric.
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[NUMERIC_COLUMNS].isna().any().any():
        bad_rows = df[df[NUMERIC_COLUMNS].isna().any(axis=1)]
        raise ValueError(
            "Non-numeric or missing values found in salary columns for "
            f"Employee_ID(s): {bad_rows['Employee_ID'].tolist()}"
        )

    df["Gross_Earnings"] = (
        df["Basic_Salary"] + df["HRA"] + df["DA"] + df["Other_Allowance"] + df["Bonus"]
    ).round(2)

    df["PF_Amount"] = round(df["Basic_Salary"] * df["PF_Percentage"] / 100, 2)
    df["Tax_Amount"] = round(df["Gross_Earnings"] * df["Tax_Percentage"] / 100, 2)

    df["NetPay"] = (df["Gross_Earnings"] - df["PF_Amount"] - df["Tax_Amount"]).round(2)

    return df


def save_dataframe(df: pd.DataFrame, output_path: str) -> None:
    """Save a DataFrame to CSV, creating the parent directory if needed."""
    ensure_dir(os.path.dirname(output_path))
    df.to_csv(output_path, index=False)


def is_valid_email(email: str) -> bool:
    """Very small, dependency-free sanity check for an email address."""
    if not isinstance(email, str):
        return False
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1] and " " not in email
