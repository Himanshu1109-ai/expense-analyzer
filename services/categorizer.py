from models.category import Category

def categorize(merchant):
    """
    Categorize a merchant into an expense category.
    
    Args:
        merchant (str): The merchant name to categorize
        
    Returns:
        str: The category of the expense
    """
    return Category.categorize(merchant)
