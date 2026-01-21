# GitHub Issue Analyzer (AI-Powered)

## Overview

This project is an AI-powered GitHub Issue Analyzer that fetches issue data from public GitHub repositories and generates structured, actionable insights using a Large Language Model (LLM).

The application converts unstructured GitHub issue discussions into a standardized JSON format to help maintainers and contributors quickly understand issue type, priority, and potential impact.

---



## Core Features

### 1. Input UI
- Simple and clean interface to input:
  - Public GitHub repository URL
  - Issue number
- Built using Streamlit for rapid prototyping and usability.

### 2. Backend Logic
- Lightweight backend implemented in Python.
- Triggers issue analysis based on user input.
- Modular separation of:
  - GitHub API data fetching
  - AI analysis logic
  - UI rendering

### 3. AI Core
- Fetches the following using GitHub REST API:
  - Issue title
  - Issue body
  - Issue comments
- Processes issue context using a Large Language Model.
- Produces output in a strict and consistent JSON schema.

### 4. Output Display
- Displays AI-generated analysis in a clean and readable format.
- Ensures structured visualization of JSON output.

---
## Usage Example (Input and Output)

The following screenshots demonstrate how the application works with real GitHub issues.

### Input Example
- Repository URL: https://github.com/facebook/react
- Issue Number: 24502

![Input Example](screenshots/input_example.png)

### AI-Generated Output

The application fetches the issue title, body, and comments from GitHub and generates a structured JSON analysis using the LLM.

![Output Example](screenshots/output_example.png)

## AI-Generated JSON Output Format

```json
{
  "summary": "A one-sentence summary of the user's problem or request.",
  "type": "bug | feature_request | documentation | question | other",
  "priority_score": "A score from 1 (low) to 5 (critical), with a brief justification for the score.",
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "A brief sentence on the potential impact on users if the issue is a bug."
}

