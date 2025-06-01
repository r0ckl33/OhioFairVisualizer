from datetime import datetime

def parse_date(date_str):
    # Supports "6/7/2025"
    return datetime.strptime(date_str, "%m/%d/%Y")

def format_date(dt):
    return dt.strftime("%m/%d/%Y")
