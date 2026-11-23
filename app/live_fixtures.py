"""Synthetic and independent reference fixtures for real-service integration.

These are NOT the RAG model's returned contexts. The integration suite ingests
this corpus via PolicyMind's actual API and then measures real retrieval.
"""
SOURCE_FILENAME = "guardeval_test_policy.pdf"
REQUIRED_DOCUMENTS = (
    "Certificate of Insurance", "WSIB Clearance", "GST/HST Registration", "Signed MSA",
)
PAGES = [
    "SYNTHETIC TEST DATA. Mistral travel policy: daily meal reimbursement ceiling is 42 CAD per travel day with itemized receipts.",
    "SYNTHETIC TEST DATA. Linden home office equipment policy: annual keyboard and monitor reimbursement limit is 375 CAD with manager approval.",
    "SYNTHETIC TEST DATA. Cedar vacation policy: first-year full-time employees accrue 14 vacation days per year.",
    "SYNTHETIC TEST DATA. Birch contractor account security policy: inactive contractor accounts must be disabled within 24 hours of contract termination.",
    "SYNTHETIC TEST DATA. Orion taxi expense policy: taxi fares greater than 90 CAD require manager preapproval before reimbursement.",
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
    {
        "id": "account-security",
        "question": "Under the Birch contractor account security policy, within how many hours of termination must accounts be disabled?",
        "reference": "24 hours",
        "page": 4,
    },
    {
        "id": "taxi-expense",
        "question": "Under the Orion taxi expense policy, what taxi amount triggers manager preapproval?",
        "reference": "90 CAD",
        "page": 5,
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
    {
        "id": "empty-documents",
        "vendor_name": "Synthetic Empty File Supplier",
        "submitted_docs": [],
        "expected_risk": "red",
        "decision": "reject",
    },
    {
        "id": "two-missing",
        "vendor_name": "Synthetic Partial File Supplier",
        "submitted_docs": ["Certificate of Insurance", "WSIB Clearance"],
        "expected_risk": "red",
        "decision": "reject",
    },
    {
        "id": "reordered-complete",
        "vendor_name": "Synthetic Reordered Supplier",
        "submitted_docs": ["Signed MSA", "GST/HST Registration", "WSIB Clearance", "Certificate of Insurance"],
        "expected_risk": "green",
        "decision": "approve",
    },
]
