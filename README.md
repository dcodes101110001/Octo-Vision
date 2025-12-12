# 🔍 Octo-Vision - Paste Site Scraper

A Python-based Streamlit application that scrapes paste sites like Pastebin.com and scans for keyword patterns. Perfect for monitoring sensitive information leaks and security concerns.

## ✨ Features

- 🔍 **Scrape Recent Pastes**: Automatically fetch recent public pastes from Pastebin
- 🎯 **Custom URL Scanning**: Scan specific paste URLs
- 📁 **CSV Keyword Upload**: Upload keyword patterns from CSV files
- ⌨️ **Manual Keyword Entry**: Enter keywords directly in the interface
- 🔎 **Pattern Matching**: Case-sensitive and case-insensitive search options
- 📊 **Detailed Results**: View matched keywords with context
- 💾 **Export Results**: Download scan results as CSV

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dcodes101110001/Octo-Vision.git
cd Octo-Vision
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Keyword Configuration

Choose between two methods to add keywords:

#### Upload CSV File
- Click "Upload CSV" in the sidebar
- Upload a CSV file with keywords in the first column
- A sample `keywords.csv` is provided as a template

#### Manual Entry
- Select "Manual Entry" in the sidebar
- Enter keywords one per line in the text area
- Click outside the text area to save

### 2. Scraping Options

#### Recent Pastebin Posts
- Select "Recent Pastebin Posts"
- Choose the number of pastes to scrape (1-20)
- Click "🚀 Start Scraping"
- Wait for results (may take time due to rate limiting)

#### Custom URL
- Select "Custom URL"
- Enter a Pastebin URL (e.g., `https://pastebin.com/xxxxx`)
- Click "🔍 Scan URL"

### 3. View Results

- Results appear in the right panel
- Expand each match to see:
  - Matched keywords
  - Context around matches
  - Full paste content
- Export results as CSV for further analysis

## 📁 File Structure

```
Octo-Vision/
├── app.py              # Main Streamlit application
├── scraper.py          # Paste site scraper module
├── scanner.py          # Keyword scanner module
├── keywords.csv        # Sample keywords file
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🔑 Sample Keywords CSV Format

```csv
keyword
password
api_key
secret_key
access_token
private_key
database
username
credentials
```

## ⚠️ Important Notes

- **Rate Limiting**: The scraper includes delays to respect Pastebin's rate limits
- **Public Pastes Only**: Only scrapes publicly available pastes
- **Ethical Use**: Use this tool responsibly and legally
- **Privacy**: Do not use this tool to harvest personal information
- **Terms of Service**: Ensure compliance with Pastebin's ToS

## 🛠️ Dependencies

- **streamlit**: Web application framework
- **requests**: HTTP library for scraping
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and CSV handling
- **lxml**: XML/HTML parser

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational purposes.

## ⚖️ Disclaimer

This tool is intended for security research and monitoring your own data leaks. Users are responsible for ensuring their use complies with applicable laws and terms of service. The authors are not responsible for any misuse of this tool.
