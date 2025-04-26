def format_number(num):
    """
    Format large numbers with commas and no decimals if
    it's an integer.
    """
    if num is None:
        return "N/A"
    try:
        if num == int(num):
            return f"{int(num):,}"
        return f"{num:,.2f}"
    
    except (ValueError, TypeError):
        return "N/A"

def format_eps(eps):
    """
    Format EPS to 2 decimal places.
    """
    if eps is None:
        return "N/A"
    try:
        return f"{float(eps):.2f}"
    
    except (ValueError, TypeError):
        return "N/A"