---
name: google-sheets-analyst
description: Read and analyze Google Sheets directly via API. Use when the user asks to "find [data] in my sheets", "analyze [spreadsheet url]", or interact with Google Sheets data without downloading files.
---

# Google Sheets Analyst

## Overview

This skill allows Gemini CLI to directly read data from Google Sheets using a Python script and the Google Sheets API. This abstracts away the complexity of downloading CSVs and provides a seamless, "natural language" interface to the user's live spreadsheets.

## Workflow: Reading a Google Sheet

When a user asks to analyze, read, or find data in a Google Sheet, follow these steps:

1.  **Identify the Target:** Extract the Google Sheet URL or ID from the user's prompt.
2.  **Execute the Script:** Run the provided Python script `scripts/read_sheet.py` using `run_shell_command`. Pass the Sheet URL/ID as an argument.
3.  **Analyze the Output:** The script will output the sheet's contents (as CSV or JSON) to `stdout`.
4.  **Respond to User:** Use the data from `stdout` to answer the user's original query (e.g., finding a specific name, summarizing data, calculating totals).

## Setup Requirements (For the User)

Before this skill can be used, the user MUST complete the one-time Google Cloud setup. If the script fails due to missing credentials, guide the user to read the `references/setup_guide.md` file included in this skill.

## Resources

-   `scripts/read_sheet.py`: The Python script that interacts with the Google Sheets API.
-   `references/setup_guide.md`: Instructions for the user on how to obtain a `credentials.json` file from Google Cloud Console.