class Category:
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education"
    GROCERIES = "Groceries"
    FUEL = "Fuel"
    OTHER = "Other"

    @staticmethod
    def categorize(merchant):
        merchant = merchant.lower().strip()

        # 🍔 Food
        if any(x in merchant for x in [
            "zomato", "swiggy", "dominos", "pizza hut",
            "kfc", "mcdonald", "burger king", "restaurant",
            "cafe", "starbucks"
        ]):
            return Category.FOOD

        # 🚕 Travel
        elif any(x in merchant for x in [
            "uber", "ola", "rapido", "irctc",
            "makemytrip", "redbus"
        ]):
            return Category.TRAVEL

        # 🛒 Shopping
        elif any(x in merchant for x in [
            "amazon", "flipkart", "myntra",
            "ajio", "meesho", "nykaa"
        ]):
            return Category.SHOPPING

        # 💡 Bills
        elif any(x in merchant for x in [
            "electric", "electricity", "bill",
            "recharge", "jio", "airtel",
            "vi", "vodafone", "bsnl"
        ]):
            return Category.BILLS

        # 🏥 Health
        elif any(x in merchant for x in [
            "apollo", "pharmacy", "hospital",
            "medplus", "1mg", "clinic"
        ]):
            return Category.HEALTH

        # 🎬 Entertainment
        elif any(x in merchant for x in [
            "netflix", "prime", "hotstar",
            "spotify", "bookmyshow", "sony liv"
        ]):
            return Category.ENTERTAINMENT

        # 📚 Education
        elif any(x in merchant for x in [
            "udemy", "coursera", "unacademy",
            "byju", "skillshare"
        ]):
            return Category.EDUCATION

        # 🥦 Groceries
        elif any(x in merchant for x in [
            "dmart", "bigbasket", "blinkit",
            "zepto", "instamart", "reliance fresh"
        ]):
            return Category.GROCERIES

        # ⛽ Fuel
        elif any(x in merchant for x in [
            "indian oil", "bharat petroleum",
            "hp petrol", "petrol", "diesel"
        ]):
            return Category.FUEL

        else:
            return Category.OTHER