"""
generate_dataset.py
--------------------
Generates a synthetic dataset of 1000 employees for the Automated Payslip
Generator project. Output columns match the sample format:

Employee_ID | Employee_Name | Department | Designation | Basic_Salary |
HRA | DA | Other_Allowance | Bonus | Tax_Percentage | PF_Percentage

Usage:
    python generate_dataset.py
Output:
    employee_dataset.csv  (created in the same folder)
"""

import csv
import random

random.seed(42)  # remove or change this for different random data each run

NUM_EMPLOYEES = 1000
OUTPUT_FILE = "employee_dataset.csv"

# ---------------------------------------------------------------------------
# Reference data pools
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Suresh", "Kavya",
    "Arjun", "Divya", "Karthik", "Pooja", "Rajesh", "Meera", "Sanjay", "Neha",
    "Vivek", "Ritu", "Manoj", "Swati", "Deepak", "Anita", "Ramesh", "Lakshmi",
    "Ajay", "Shreya", "Naveen", "Pallavi", "Gopal", "Sunita", "Harish", "Asha",
    "Praveen", "Madhuri", "Sandeep", "Geetha", "Vinay", "Rekha", "Mahesh", "Usha",
    "Arvind", "Nisha", "Srinivas", "Bhavna", "Kiran", "Sarita", "Naresh", "Komal",
    "Yogesh", "Tanvi", "Abhishek", "Jyoti", "Girish", "Sapna", "Pradeep", "Kavita",
    "Anil", "Roopa", "Subash", "Vandana", "Ashok", "Preeti", "Dinesh", "Shilpa",
    "Mohit", "Aishwarya", "Ravi", "Deepa", "Sunil", "Rashmi", "Gaurav", "Manisha",
    "Vijay", "Soumya", "Akash", "Charu", "Ramana", "Hema", "Satish", "Aarti",
]

LAST_NAMES = [
    "Sharma", "Verma", "Iyer", "Reddy", "Singh", "Gupta", "Nair", "Patel",
    "Mehta", "Joshi", "Kulkarni", "Das", "Rao", "Pillai", "Menon", "Chatterjee",
    "Bose", "Mukherjee", "Saxena", "Agarwal", "Bhat", "Krishnan", "Pandey",
    "Trivedi", "Naidu", "Chauhan", "Kapoor", "Malhotra", "Ghosh", "Sinha",
    "Raman", "Subramanian", "Venkatesh", "Acharya", "Bhatt", "Desai", "Shetty",
    "Yadav", "Mishra", "Tiwari",
]

DEPARTMENTS_DESIGNATIONS = {
    "IT": [
        "Software Engineer", "Senior Software Engineer", "Tech Lead",
        "QA Engineer", "DevOps Engineer", "System Administrator",
    ],
    "HR": [
        "HR Executive", "HR Manager", "Recruiter", "HR Generalist",
    ],
    "Finance": [
        "Accountant", "Financial Analyst", "Finance Manager", "Auditor",
    ],
    "Sales": [
        "Sales Executive", "Sales Manager", "Business Development Executive",
        "Regional Sales Head",
    ],
    "Marketing": [
        "Marketing Executive", "Marketing Manager", "Content Strategist",
        "SEO Specialist",
    ],
    "Operations": [
        "Operations Executive", "Operations Manager", "Logistics Coordinator",
    ],
    "Admin": [
        "Admin Executive", "Office Manager", "Front Desk Executive",
    ],
    "R&D": [
        "Research Associate", "Research Scientist", "R&D Manager",
    ],
}

SENIOR_KEYWORDS = ["Manager", "Lead", "Head", "Scientist", "Senior"]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

SALARY_RANGES = {
    "Software Engineer": (50000, 70000),
    "Senior Software Engineer": (80000, 110000),
    "Tech Lead": (100000, 130000),
    "QA Engineer": (40000, 60000),
    "DevOps Engineer": (60000, 90000),
    "System Administrator": (45000, 65000),

    "HR Executive": (35000, 50000),
    "HR Generalist": (40000, 60000),
    "Recruiter": (35000, 55000),
    "HR Manager": (80000, 100000),

    "Accountant": (40000, 60000),
    "Financial Analyst": (50000, 75000),
    "Finance Manager": (90000, 120000),
    "Auditor": (45000, 65000),

    "Sales Executive": (35000, 55000),
    "Business Development Executive": (40000, 65000),
    "Sales Manager": (80000, 110000),
    "Regional Sales Head": (120000, 150000),

    "Marketing Executive": (35000, 55000),
    "SEO Specialist": (45000, 65000),
    "Content Strategist": (50000, 70000),
    "Marketing Manager": (80000, 110000),

    "Operations Executive": (35000, 55000),
    "Logistics Coordinator": (40000, 60000),
    "Operations Manager": (80000, 110000),

    "Admin Executive": (30000, 45000),
    "Front Desk Executive": (25000, 40000),
    "Office Manager": (60000, 85000),

    "Research Associate": (50000, 70000),
    "Research Scientist": (90000, 120000),
    "R&D Manager": (110000, 140000),
}

def random_basic_salary(designation: str) -> int:
    low, high = SALARY_RANGES[designation]
    return random.randrange(low, high + 1, 500)


def round_to_nearest(value: float, nearest: int = 50) -> int:
    """Round a number to the nearest multiple (e.g. 4500, 6550, 7800)."""
    return int(round(value / nearest) * nearest)


def calc_allowances(basic_salary: int):
    """Calculate HRA, DA, Other Allowance and Bonus based on basic salary,
    rounded to the nearest 50 so the figures look clean on a payslip."""
    hra = round_to_nearest(basic_salary * random.uniform(0.18, 0.22))
    da = round_to_nearest(basic_salary * random.uniform(0.08, 0.12))
    other_allowance = round_to_nearest(basic_salary * random.uniform(0.04, 0.08))
    bonus = round_to_nearest(basic_salary * random.uniform(0.05, 0.15))

    # 40% of employees receive a bonus
    if random.random() < 0.40:
        bonus = round_to_nearest(
            basic_salary * random.uniform(0.05, 0.15)
        )
    else:
        bonus = 0

    return hra, da, other_allowance, bonus


def random_percentages():
    """Tax and PF percentages within realistic Indian payroll ranges."""
    tax_percentage = random.choice([0, 5, 10, 15, 20])
    pf_percentage = 12  # standard PF rate in India
    return tax_percentage, pf_percentage


def generate_unique_name(used_names: set) -> str:
    """Generate a full name, allowing repeats only after pool exhaustion."""
    while True:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used_names or len(used_names) >= len(FIRST_NAMES) * len(LAST_NAMES):
            used_names.add(name)
            return name


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_dataset(num_employees: int = NUM_EMPLOYEES):
    rows = []
    used_names = set()
    id_width = max(3, len(str(num_employees)))

    for i in range(1, num_employees + 1):
        employee_id = f"EMP{i:0{id_width}d}"
        employee_name = generate_unique_name(used_names)
        department = random.choice(list(DEPARTMENTS_DESIGNATIONS.keys()))
        designation = random.choice(DEPARTMENTS_DESIGNATIONS[department])

        basic_salary = random_basic_salary(designation)
        hra, da, other_allowance, bonus = calc_allowances(basic_salary)
        tax_percentage, pf_percentage = random_percentages()

        rows.append({
            "Employee_ID": employee_id,
            "Employee_Name": employee_name,
            "Department": department,
            "Designation": designation,
            "Basic_Salary": basic_salary,
            "HRA": hra,
            "DA": da,
            "Other_Allowance": other_allowance,
            "Bonus": bonus,
            "Tax_Percentage": tax_percentage,
            "PF_Percentage": pf_percentage,
        })

    return rows


def write_csv(rows, output_file: str = OUTPUT_FILE):
    fieldnames = [
        "Employee_ID", "Employee_Name", "Department", "Designation",
        "Basic_Salary", "HRA", "DA", "Other_Allowance", "Bonus",
        "Tax_Percentage", "PF_Percentage",
    ]
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = generate_dataset(NUM_EMPLOYEES)
    write_csv(data, OUTPUT_FILE)
    print(f"Generated {len(data)} employee records.")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nSample row:")
    print(data[0])
