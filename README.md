# Assignment Grader

An automated tool to grade assignments

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
4. Update the `.env` file with your credentials:
   ```
   EMAIL=your_email@example.com
   PASSWORD=your_password
   ```
5. Create a venv:
   ```bash
      python -m venv venv
      source venv/bin/activate
   ```
## Usage

Run the grader:
```bash
python grader.py
```

## Features

- Automated login to platform
- Navigation to assignments section
- Identification of assignments requiring review
- Automated grading process
- Error handling and logging 
