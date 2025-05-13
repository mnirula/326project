import os
import openai


class OpenAIEngine:
    def __init__(self, api_key: str = None):
        # Use provided API key or fallback to environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key.")
        openai.api_key = self.api_key  # Set the API key for OpenAI library


    def get_keywords(self, job_description: str, num_keywords: int = 10):
        # Prompt to request key skills/keywords with weights in JSON format
        prompt = (
            f"Extract {num_keywords} key skills or qualifications from the following job description. "
            f"Provide each with a weight (out of 100) that reflects its importance, and ensure the weights sum to 100. "
            f"Respond in JSON format as an array of objects, each with 'keyword' and 'weight'.\n"
            f"Job Description:\n{job_description}"
        )


        try:
            # Make a request to OpenAI ChatCompletion
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")


        # Get the response text
        content = response.choices[0].message.content.strip()


        import json
        try:
            # Attempt to parse the JSON result
            keywords_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing if response isn't valid JSON
            keywords_data = []
            for line in content.splitlines():
                line = line.strip().strip(",")
                if not line:
                    continue
                if ":" in line:
                    parts = line.split(":", 1)
                elif "-" in line:
                    parts = line.split("-", 1)
                else:
                    parts = line.split(None, 1)
                if len(parts) == 2:
                    key = parts[0].strip().strip('"').strip("'")
                    wt = parts[1].strip().strip("%").strip()
                    wt = "".join(ch for ch in wt if ch.isdigit())
                    weight_val = int(wt) if wt.isdigit() else 0
                    if key:
                        keywords_data.append({"keyword": key, "weight": weight_val})


        # Process parsed results into clean keyword-weight pairs
        keywords_list = []
        for item in keywords_data:
            if not isinstance(item, dict):
                continue
            key = str(item.get("keyword", "")).strip()
            weight = item.get("weight", 0)
            try:
                weight = int(weight)
            except:
                try:
                    weight = int(float(weight))
                except:
                    weight = 0
            if key:
                keywords_list.append({"keyword": key, "weight": weight})


        # Normalize weights to sum to 100, if necessary
        total = sum(item["weight"] for item in keywords_list)
        if total > 0 and total != 100:
            for kw in keywords_list:
                kw["weight"] = int(round(kw["weight"] / total * 100))


        return keywords_list





