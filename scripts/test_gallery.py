#!/usr/bin/env python3
"""Maintenance-only DOM smoke test for 02-references/gallery; run on request."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def skipped(reason: str) -> int:
    print(
        json.dumps(
            {
                "status": "SKIP",
                "scope": "Maintenance-only gallery DOM smoke test",
                "reason": reason,
                "tests": [],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(argv)
    gallery = args.root.resolve() / "02-references/gallery/index.html"
    if not gallery.is_file():
        return skipped(f"Không tìm thấy gallery: {gallery}")
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return skipped("Playwright không có trong môi trường; không tự cài dependency.")

    result: dict[str, object] = {"tests": []}
    try:
        with sync_playwright() as playwright:
            launch_options: dict[str, object] = {
                "headless": True,
                "args": ["--no-sandbox"],
            }
            chromium_path = os.environ.get("AIA_CHROMIUM")
            if chromium_path:
                launch_options["executable_path"] = chromium_path
            browser = playwright.chromium.launch(**launch_options)
            page = browser.new_page(
                viewport={"width": 1600, "height": 1000}, device_scale_factor=1
            )
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.set_content(
                gallery.read_text(encoding="utf-8"), wait_until="domcontentloaded"
            )
            page.wait_for_timeout(300)

            def test(name: str, condition: bool) -> None:
                result["tests"].append(
                    {"name": name, "status": "PASS" if condition else "FAIL"}
                )

            test("DOM có mười bảng nhóm", page.locator(".board:visible").count() == 10)
            page.select_option("#group", "G09")
            test("Nhóm infographic có hai bảng", page.locator(".board:visible").count() == 2)
            page.click("#viewSamples")
            test("Nhóm infographic có mười hai mẫu", page.locator(".sample:visible").count() == 12)
            page.select_option("#topology", "vong-lap")
            test(
                "Kết hợp G09 và vòng lặp ra I01",
                page.locator(".sample:visible").count() == 1
                and "I01" in page.locator(".sample:visible h2").inner_text(),
            )
            page.click("#reset")
            page.fill("#q", "vong lap")
            test("Tìm tiếng Việt không dấu", page.locator(".sample:visible").count() == 2)
            page.click("#reset")
            page.select_option("#group", "G06")
            page.select_option("#phase", "evidence")
            test("Lọc dữ liệu và bằng chứng", page.locator(".sample:visible").count() == 6)
            page.click("#reset")
            page.select_option("#rep", "illustrated")
            test("Loại mẫu minh họa", page.locator(".sample:visible").count() == 12)
            test("Không có lỗi JavaScript", not errors)
            browser.close()
    except PlaywrightError as exc:
        return skipped(f"Playwright/browser không chạy được: {exc}")

    result["status"] = (
        "PASS"
        if all(test["status"] == "PASS" for test in result["tests"])
        else "FAIL"
    )
    result["errors"] = errors
    result["scope"] = (
        "Maintenance-only JavaScript/DOM filtering via page.set_content; "
        "active file links are checked by validate.py."
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
