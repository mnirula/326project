import re
from models import Resume


class Analyzer:
    """Analyzes the resume against the weighted keywords to compute a compatibility score."""
    def __init__(self, resume: Resume, keywords: list):
        self.resume = resume
        self.keywords = keywords  # list of dictionaries with "keyword" and "weight"


    def analyze(self):
        """
        Compare the resume content with the keywords.
        Returns a tuple: (score, missing_keywords_list).
        """
        if not self.keywords:
            return 0, []  # Return 0 score and empty list if no keywords provided


        # Convert entire resume text to lowercase for case-insensitive comparison
        raw_text = self.resume.all_text().lower()
        # Clean text by replacing non-alphanumeric characters with spaces for broader matching
        clean_text = re.sub(r'[^a-z0-9]+', ' ', raw_text)


        total_score = 0
        missing_keywords = []


        for item in self.keywords:
            # Extract and clean keyword
            kw = str(item.get("keyword", "")).strip().lower()
            if not kw:
                continue  # Skip if keyword is empty


            # Safely extract weight and convert to integer
            try:
                weight = int(item.get("weight", 0))
            except:
                try:
                    weight = int(float(item.get("weight", 0)))
                except:
                    weight = 0  # Default to 0 if conversion fails


            # Check if keyword exists in either raw or cleaned resume text
            if kw in raw_text or kw in clean_text:
                total_score += weight  # Add weight to total score
            else:
                # Append original keyword to missing list
                missing_keywords.append(kw if item.get("keyword") is None else item["keyword"])


        # Ensure score does not exceed 100
        if total_score > 100:
            total_score = 100


        return total_score, missing_keywords  # Return final score and list of missing keywords



