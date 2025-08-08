import yaml
import os
from openai import OpenAI
# You would typically import your LLM client here, e.g., from openai import OpenAI

def load_config():
    """
    Loads configuration from config.yaml file.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: config.yaml not found at {config_path}. Using default values.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}. Using default values.")
        return {}

class LLMService:
    def __init__(self):
        self.config = load_config()
        self.llm_config = self.config.get('llm', {})
        self.api_key = self.llm_config.get('api_key')
        self.model_name = self.llm_config.get('model_name', 'gpt-5')
        self.api_base = self.llm_config.get('api_base') # For custom API endpoints
        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_base
        )

        # Initialize your LLM client here
        # Example for OpenAI:
        # if self.api_key:
        #     self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        # else:
        #     self.client = None
        #     print("Warning: LLM API key not found in config.yaml. LLM functions will return placeholders.")

    def summarize_text(self, text: str) -> str:
        """
        Summarizes the given text using the configured LLM.
        """
        if not self.api_key:
            return f"Placeholder Summary: {text[:100]}..." # Return placeholder if no API key

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes news articles concisely. Output format: Summary: <summary>"},
                    {"role": "user", "content": f"Please summarize the following news article:\n\n{text}"}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error summarizing text with LLM: {e}")
            return f"Error Summary: Failed to summarize due to LLM error. Original text start: {text[:100]}..."
        
        # Placeholder implementation
        return f"Summary of: {text[:200]}..." if text else "No content to summarize."

    def generate_daily_report(self, news_summaries: list) -> str:
        """
        Generates a daily report based on a list of news summaries.
        """
        if not self.api_key:
            return "Placeholder Daily Report: LLM API key not configured."

        if not news_summaries:
            return "No news summaries provided for daily report."

        report_content = "Daily News Report:\n\n"
        for i, item in enumerate(news_summaries):
            report_content += f"{i+1}. {item.get('title', 'No Title')}\n"
            report_content += f"   Summary: {item.get('summary', 'No Summary')}\n"
#            report_content += f"   Published: {item.get('published_at', 'N/A')}\n"
#            report_content += f"   Link: {item.get('link', 'N/A')}\n\n"
        
        # Example LLM call for daily report (replace with your actual LLM client logic)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Generate a concise daily news report based on the provided summaries. Highlight key trends or important events."},
                    {"role": "user", "content": f"Here are the news summaries for today:\n\n{report_content}\n\nPlease generate a comprehensive daily report."}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating daily report with LLM: {e}")
            return f"Error Daily Report: Failed to generate due to LLM error. Summaries provided: {len(news_summaries)}"


if __name__ == '__main__':
    # Example usage
    llm_service = LLMService()
    
    # Test summarization
    sample_text = "Apple Inc. announced record quarterly earnings today, driven by strong iPhone sales and growth in its services division. The company's stock price surged in after-hours trading."
    summary = llm_service.summarize_text(sample_text)
    print(f"Sample Summary: {summary}\n")

    # Test daily report generation
    sample_summaries = [
        {"title": "Apple Earnings Beat Expectations", "summary": "Apple reported strong earnings, driven by iPhone and services.", "published_at": "2025-08-01 10:00:00 UTC", "link": "http://example.com/apple"},
        {"title": "Tech Stocks Rally", "summary": "Overall tech sector saw gains today.", "published_at": "2025-08-01 11:30:00 UTC", "link": "http://example.com/tech"}
    ]
    daily_report = llm_service.generate_daily_report(sample_summaries)
    print(f"Sample Daily Report:\n{daily_report}")
