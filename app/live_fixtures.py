"""Synthetic and independent reference fixtures for real-service integration.

These are NOT the RAG model's returned contexts. The integration suite ingests
this corpus via PolicyMind's actual API and then measures real retrieval.
"""
SOURCE_FILENAME = "guardeval_test_policy.pdf"
PAGES = [
    "SYNTHETIC TEST DATA. Mistral travel policy: daily meal reimbursement ceiling is 42 CAD per travel day with itemized receipts.",
    "SYNTHETIC TEST DATA. Linden home office equipment policy: annual keyboard and monitor reimbursement limit is 375 CAD with manager approval.",
    "SYNTHETIC TEST DATA. Cedar vacation policy: first-year full-time employees accrue 14 vacation days per year.",
]
RAG_CASES = [
    {
        "id": "travel-meals",
        "question": "Under the Mistral travel policy, what is the daily meal reimbursement ceiling?",
        "reference": "42 CAD",
        "page": 1,
    },
    {
        "id": "office-equipment",
        "question": "Under the Linden equipment policy, what is the annual reimbursement limit?",
        "reference": "375 CAD",
        "page": 2,
    },
    {
        "id": "vacation-days",
        "question": "Under the Cedar vacation policy, how many vacation days do first-year employees accrue?",
        "reference": "14 vacation days",
        "page": 3,
    },
]
FLOW_CASES = [
    {
        "id": "complete",
        "vendor_name": "Synthetic Complete Supplier",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance", "GST/HST Registration", "Signed MSA"],
        "expected_risk": "green",
        "decision": "approve",
    },
    {
        "id": "single-missing",
        "vendor_name": "Synthetic Incomplete Supplier",
        "submitted_docs": ["Certificate of Insurance", "GST/HST Registration", "Signed MSA"],
        "expected_risk": "yellow",
        "decision": "reject",
    },
    {
        "id": "high-risk",
        "vendor_name": "Synthetic High Risk Supplier",
        "submitted_docs": ["GST/HST Registration"],
        "expected_risk": "red",
        "decision": "reject",
    },
]
