import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


import os
from dotenv import load_dotenv
from simply_beam_system.steps.preliminary_sizing import PreliminarySizing  # CORRECTED IMPORT
from simply_beam_system.core.exceptions import DesignError, InputError

def main():
    """Main function to demonstrate the workflow."""

    # --- Get API Key from Environment Variable ---
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("DEEPSEEK_API_KEY")

    # Validate the key format (basic check)
    if not api_key:
        print("Error: DEEPSEEK_API_KEY environment variable not found.  Please set it or create a .env file.")
        return

    # --- Design Mode ---
    designer = PreliminarySizing()
    try:
        span_length = float(input("Enter the span length in inches (e.g., 240 for 20ft): "))
        design_parameters = {"span_length": span_length}
        design_results = designer.design(design_parameters)
        print("\nPreliminary Design Results:")
        print(design_results)  # Print the raw results

        # --- Interact with LLM ---
        llm_response = designer.request_llm_feedback(design_results, api_key)
        print("\nLLM Response:")
        print(llm_response)

    except (ValueError, InputError) as e:
        print(f"Input Error: {e}")
    except DesignError as e:
        print(f"Design Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()