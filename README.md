# Tutly Assignment Grader

An automated tool to grade assignments on the Tutly learning platform.

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Chrome WebDriver (automatically managed by webdriver-manager)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Update the `.env` file with your Tutly credentials:
   ```
   TUTLY_EMAIL=your_email@example.com
   TUTLY_PASSWORD=your_password
   ```

## Usage

Run the grader:
```bash
python tutly_grader.py
```

## Features

- Automated login to Tutly platform
- Navigation to assignments section
- Identification of assignments requiring review
- Automated grading process
- Error handling and logging 