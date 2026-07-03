"""
main.py
--------
Orchestrates the full Automated Payslip Generator pipeline:

1. Load employee data (CSV/Excel)
2. Calculate Net Pay for everyone and save employees_with_netpay.csv
3. Generate a PDF payslip per employee
4. Email the PDF to each employee
5. Write a manifest CSV logging the outcome for every employee

Run this from the project root with:  python run.py
(or directly with:                    python src/main.py)
"""

from operator import index
from operator import index
import os
import sys

import pandas as pd
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()

# Allow running this file directly (python src/main.py) by making sure
# the src/ folder is on the path for sibling imports.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_employee_data, calculate_net_pay, save_dataframe, ensure_dir, is_valid_email
from pdf_generator import generate_payslip_pdf
from email_sender import send_payslip_email


# ---------------------------------------------------------------------------
# Configuration — edit these as needed, or later swap for argparse/env vars.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "employees.csv")        # or employees.xlsx
NETPAY_CSV = os.path.join(PROJECT_ROOT, "data", "employees_with_netpay.csv")
PAYSLIP_DIR = os.path.join(PROJECT_ROOT, "output", "payslips")
MANIFEST_CSV = os.path.join(PROJECT_ROOT, "output", "logs", "payslip_manifest.csv")

PAYSLIP_MONTH = "July"
PAYSLIP_YEAR = "2026"

SEND_EMAILS = True   # Set to False to only generate PDFs without emailing.

TEST_MODE = True  # Set to True to send all emails to TEST_EMAIL_ADDRESS instead of the real employee emails.
TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL") if TEST_MODE else None  # Only used if TEST_MODE is True.

def run_pipeline():
    print("=" * 60)
    print(" AUTOMATED PAYSLIP GENERATOR")
    print("=" * 60)

    # 1. Load employee data -------------------------------------------------
    try:
        print(f"\n[1/5] Loading employee data from: {INPUT_FILE}")
        df = load_employee_data(INPUT_FILE)
        print(f"      Loaded {len(df)} employee record(s).")
    except (FileNotFoundError, ValueError) as e:
        print(f"      ERROR: {e}")
        return

    # 2. Calculate Net Pay ---------------------------------------------------
    try:
        print("\n[2/5] Calculating Net Pay for all employees...")
        df = calculate_net_pay(df)
        save_dataframe(df, NETPAY_CSV)
        print(f"      Saved updated data to: {NETPAY_CSV}")
    except ValueError as e:
        print(f"      ERROR: {e}")
        return

    # 3–5. Generate PDF, send email, and log each employee ------------------
    print("\n[3/5] Generating PDF payslips...")
    print("[4/5] Sending emails (SEND_EMAILS = {})...".format(SEND_EMAILS))
    ensure_dir(PAYSLIP_DIR)
    ensure_dir(os.path.dirname(MANIFEST_CSV))

    manifest_rows = []

    for index, (_, row) in enumerate(df.iterrows()):
        employee = row.to_dict()
        emp_id = employee.get("Employee_ID")
        name = employee.get("Employee_Name")
        email = employee.get("Email")
        net_pay = employee.get("NetPay")

        pdf_path = ""
        email_status = "Skipped"

        # --- Generate PDF ---
        try:
            pdf_path = generate_payslip_pdf(employee, PAYSLIP_MONTH, PAYSLIP_YEAR, PAYSLIP_DIR)
            print(f"      Generated payslip for {name} ({emp_id}) -> {pdf_path}")
        except Exception as e:
            print(f"      ERROR generating PDF for {name} ({emp_id}): {e}")
            manifest_rows.append({
                "Employee_ID": emp_id, "Employee_Name": name, "Email": email,
                "NetPay": net_pay, "FilePath": "", "EmailStatus": f"Failed: PDF error ({e})",
            })
            continue  # can't email without a PDF

        # --- Validate email before attempting to send ---
        if not is_valid_email(email):
            email_status = "Failed: invalid or missing email address"
            print(f"      WARNING: {name} ({emp_id}) has an invalid email — skipping send.")
        elif SEND_EMAILS:
            if TEST_MODE:
                if index == 0:
                    print(f"      TEST MODE: Sending email for {name} ({emp_id}) to TEST_EMAIL_ADDRESS: {TEST_EMAIL_ADDRESS}")
                    email_status = send_payslip_email(employee, pdf_path, PAYSLIP_MONTH, PAYSLIP_YEAR, to_email=TEST_EMAIL_ADDRESS)
            else:
                email_status = send_payslip_email(employee, pdf_path, PAYSLIP_MONTH, PAYSLIP_YEAR)
            print(f"      Email status for {name}: {email_status}")
        else:
            email_status = "Skipped (SEND_EMAILS disabled)"

        manifest_rows.append({
            "Employee_ID": emp_id, "Employee_Name": name, "Email": email,
            "NetPay": net_pay, "FilePath": pdf_path, "EmailStatus": email_status,
        })

    # --- Save manifest ---
    print("\n[5/5] Writing manifest log...")
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_df.to_csv(MANIFEST_CSV, index=False)
    print(f"      Manifest saved to: {MANIFEST_CSV}")

    print("\n" + "=" * 60)
    print(" DONE. {} payslip(s) processed.".format(len(manifest_rows)))
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
