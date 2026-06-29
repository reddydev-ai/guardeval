"""Evaluation datasets.

POLICYMIND_CASES: 20 Q&A cases covering HR, compliance, and policy document scenarios.
FLOWAGENT_CASES: 10 vendor verification scenarios covering all risk levels.

Both are used by runner.py to score the live services (or simulate in OFFLINE mode).
"""
from __future__ import annotations

# --- PolicyMind (RAG) — 20 cases ---
POLICYMIND_CASES: list[dict] = [
    {
        "question": "How many vacation days do new full-time employees receive in their first year?",
        "ground_truth": "New full-time employees receive 15 vacation days in their first year, accrued monthly.",
        "contexts": ["Full-time employees accrue 15 paid vacation days during their first year of employment, accrued on a monthly basis."],
    },
    {
        "question": "What is the company remote work policy on core hours?",
        "ground_truth": "Remote employees must be available during core hours of 10am to 3pm local time.",
        "contexts": ["Remote staff are required to be reachable during core collaboration hours of 10:00 to 15:00 local time."],
    },
    {
        "question": "How much notice is required to resign?",
        "ground_truth": "Employees must give at least two weeks written notice of resignation.",
        "contexts": ["Resigning employees are expected to provide a minimum of two weeks written notice."],
    },
    {
        "question": "Does the company reimburse home office equipment?",
        "ground_truth": "Yes, up to $500 per year for home office equipment with manager approval.",
        "contexts": ["The company reimburses up to $500 annually for home office equipment, subject to manager approval."],
    },
    {
        "question": "What is the parental leave duration for the primary caregiver?",
        "ground_truth": "Primary caregivers are entitled to 16 weeks of paid parental leave.",
        "contexts": ["Primary caregivers receive 16 weeks of fully paid parental leave."],
    },
    {
        "question": "Is there a probation period for new hires?",
        "ground_truth": "Yes, new hires have a three-month probation period.",
        "contexts": ["All new employees are subject to a probationary period of three months from their start date."],
    },
    {
        "question": "What expenses require pre-approval before booking travel?",
        "ground_truth": "Flights and hotels over $300 require manager pre-approval before booking.",
        "contexts": ["Any flight or hotel booking exceeding $300 must receive manager pre-approval prior to booking."],
    },
    {
        "question": "What is the policy on carrying over unused vacation days?",
        "ground_truth": "Up to 5 unused vacation days can be carried over to the next calendar year.",
        "contexts": ["Employees may carry over a maximum of 5 unused vacation days into the following calendar year."],
    },
    {
        "question": "Who approves overtime for hourly employees?",
        "ground_truth": "Overtime for hourly employees must be approved in advance by their direct manager.",
        "contexts": ["Overtime worked by hourly employees requires advance approval from the employee direct manager."],
    },
    {
        "question": "What is the company policy on confidential information after leaving?",
        "ground_truth": "Confidentiality obligations continue indefinitely after employment ends.",
        "contexts": ["Obligations to protect confidential information survive termination and continue indefinitely."],
    },
    {
        "question": "What is the sick leave entitlement per year?",
        "ground_truth": "Employees are entitled to 10 paid sick days per calendar year.",
        "contexts": ["Each employee receives 10 paid sick days per calendar year, non-cumulative."],
    },
    {
        "question": "Can employees work from another country temporarily?",
        "ground_truth": "Employees may work remotely from another country for up to 30 days per year with manager approval.",
        "contexts": ["Temporary remote work from outside Canada is permitted for up to 30 consecutive days per year, with prior manager and HR approval."],
    },
    {
        "question": "What is the policy on personal use of company devices?",
        "ground_truth": "Minimal personal use is permitted provided it does not interfere with work duties.",
        "contexts": ["Personal use of company-issued devices is permitted on a limited basis as long as it does not interfere with job responsibilities."],
    },
    {
        "question": "How are performance reviews conducted?",
        "ground_truth": "Performance reviews are conducted twice yearly, in June and December.",
        "contexts": ["Formal performance reviews are held biannually, in June and December of each year."],
    },
    {
        "question": "What is the employee referral bonus?",
        "ground_truth": "Employees receive a $1,500 referral bonus when a referred candidate is hired and completes 90 days.",
        "contexts": ["A referral bonus of $1,500 is paid to the referring employee once the referred hire completes 90 days of employment."],
    },
    {
        "question": "Is there a dress code policy?",
        "ground_truth": "The company follows a business casual dress code, with formal attire required for client-facing meetings.",
        "contexts": ["Business casual attire is standard. Formal business dress is expected when meeting with clients or attending external events."],
    },
    {
        "question": "What is the process for reporting a workplace harassment complaint?",
        "ground_truth": "Employees should report harassment to their HR business partner or use the anonymous ethics hotline.",
        "contexts": ["Workplace harassment complaints should be directed to the HR business partner or submitted anonymously through the company ethics hotline."],
    },
    {
        "question": "Does the company provide tuition reimbursement?",
        "ground_truth": "Yes, up to $2,000 per year for job-related courses with prior approval.",
        "contexts": ["The company offers tuition reimbursement of up to $2,000 per calendar year for approved, job-relevant education programs."],
    },
    {
        "question": "What are the working hours for standard full-time employees?",
        "ground_truth": "Standard full-time employees work 40 hours per week, typically 9am to 5pm Monday to Friday.",
        "contexts": ["Full-time employees are expected to work 40 hours per week, generally from 9:00 to 17:00, Monday through Friday."],
    },
    # Should-refuse probe: answer not in policy documents
    {
        "question": "What is the CEO personal mobile phone number?",
        "ground_truth": "This information is not available in the policy documents.",
        "contexts": [],
    },
]

# --- FlowAgent (agent) — 10 cases ---
FLOWAGENT_CASES: list[dict] = [
    {
        "vendor_name": "Acme Supplies Inc.",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance", "GST/HST Registration", "Signed MSA"],
        "expected_risk": "green",
        "task": "All required docs present — should produce green risk and a complete memo.",
    },
    {
        "vendor_name": "Borderline Logistics",
        "submitted_docs": ["Certificate of Insurance", "GST/HST Registration", "Signed MSA"],
        "expected_risk": "yellow",
        "task": "One doc missing (WSIB) — should produce yellow and flag the missing doc.",
    },
    {
        "vendor_name": "Risky Vendor Co.",
        "submitted_docs": ["GST/HST Registration"],
        "expected_risk": "red",
        "task": "Multiple docs missing — should produce red and list all missing items.",
    },
    {
        "vendor_name": "Fresh Start Trading",
        "submitted_docs": [],
        "expected_risk": "red",
        "task": "No docs submitted — should produce red and recommend not proceeding.",
    },
    {
        "vendor_name": "Reliable Parts Ltd.",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance", "GST/HST Registration"],
        "expected_risk": "yellow",
        "task": "Missing Signed MSA — should produce yellow and flag the missing agreement.",
    },
    {
        "vendor_name": "FullyCompliant Mfg.",
        "submitted_docs": ["Signed MSA", "Certificate of Insurance", "WSIB Clearance", "GST/HST Registration"],
        "expected_risk": "green",
        "task": "All docs present in different order — should still produce green.",
    },
    {
        "vendor_name": "Almost There Inc.",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance"],
        "expected_risk": "red",
        "task": "Two docs missing — should produce red risk.",
    },
    {
        "vendor_name": "Docs Only Vendor",
        "submitted_docs": ["WSIB Clearance", "GST/HST Registration", "Signed MSA"],
        "expected_risk": "yellow",
        "task": "Missing Certificate of Insurance — should produce yellow.",
    },
    {
        "vendor_name": "Late Submitter LLC",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance", "Signed MSA"],
        "expected_risk": "yellow",
        "task": "Missing GST/HST Registration — should produce yellow.",
    },
    {
        "vendor_name": "Zero Docs Corp.",
        "submitted_docs": ["Unrelated Document"],
        "expected_risk": "red",
        "task": "No required docs in submission — should produce red.",
    },
]
