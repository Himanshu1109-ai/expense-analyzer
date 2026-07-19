class Category:
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education"
    OTHER = "Other"

    @staticmethod
    def categorize(merchant):
        merchant = merchant.lower()

        if any(x in merchant for x in ["zomato", "swiggy", "restaurant"]):
            return Category.FOOD

        elif any(x in merchant for x in ["uber", "ola", "rapido"]):
            return Category.TRAVEL

        elif any(x in merchant for x in ["amazon", "flipkart", "myntra"]):
            return Category.SHOPPING

        elif any(x in merchant for x in ["electric", "bill", "recharge", "jio", "airtel", "bsnl"]):
            return Category.BILLS

        elif any(x in merchant for x in ["pharmacy", "hospital", "apollo"]):
            return Category.HEALTH

        elif any(x in merchant for x in ["netflix", "prime", "hotstar", "spotify"]):
            return Category.ENTERTAINMENT

        elif any(x in merchant for x in ["udemy", "coursera"]):
            return Category.EDUCATION

        else:
            return Category.OTHER