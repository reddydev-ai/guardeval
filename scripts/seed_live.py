"""Ingest a synthetic, versioned PDF through the real protected PolicyMind API.

For disposable CI environments only. Never seed an existing production index.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import httpx
import fitz

from app.live_fixtures import PAGES, SOURCE_FILENAME


def seed() -> None:
    url = os.environ["POLICYMIND_URL"].rstrip("/")
    key = os.environ["POLICYMIND_API_KEY"]
    if not url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise RuntimeError("Seeding is restricted to a disposable local service")
    if not key:
        raise RuntimeError("Missing POLICYMIND_API_KEY")

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / SOURCE_FILENAME
        with fitz.open() as pdf:
            for paragraph in PAGES:
                page = pdf.new_page(width=595, height=842)
                page.insert_textbox(fitz.Rect(50, 70, 545, 260), paragraph, fontsize=11)
            pdf.save(path)
        with httpx.Client(timeout=180) as client:
            with path.open("rb") as stream:
                response = client.post(
                    f"{url}/ingest",
                    headers={"X-API-Key": key},
                    files={"file": (SOURCE_FILENAME, stream, "application/pdf")},
                )
            response.raise_for_status()
            payload = response.json()
            if payload.get("chunks_indexed", 0) < len(PAGES):
                raise AssertionError("Expected at least one chunk for every synthetic page")
            if payload.get("filename") != SOURCE_FILENAME:
                raise AssertionError("Unexpected ingested source name")
            print(f"Seeded {payload['chunks_indexed']} real-index chunks from {len(PAGES)} synthetic PDF pages")


if __name__ == "__main__":
    seed()

