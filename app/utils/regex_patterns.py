patterns = {
    "Invoice ID": r"Invoice\s*#\s*[-–—]\s*(\d+)",
    "Customer ID": r"Customer ID\s*[-–—]\s*([\w\d]+)",
    "Customer Email ID": r"([\w.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    "Subscription ID": r"SUBSCRIPTION\s+ID\s*[-–—]\s*([\w\d]+)"
}