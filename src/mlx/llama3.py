import mlx.core as mx
from mlx_lm import load, generate
from pathlib import Path
import sys

def summarize(file: str, max_lines: int = 20) -> str:
    """
    Summarize text from a file using MLX LLM.
    
    Args:
        file (str): Path to the input text file
        max_lines (int): Maximum number of lines to process (default: 20)
        
    Returns:
        str: Generated summary
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: For other errors during processing
    """
    try:
        # Load model and tokenizer
        model, tokenizer = load("mlx-community/Meta-Llama-3-8B-Instruct-4bit")

        # Read input file
        file_path = Path(file)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file}")
            
        with open(file_path, "r") as f:
            lines = f.readlines()[:max_lines]
        
        text = "".join(lines)
        prompt = f"""Below is a text that needs to be summarized. Please provide a clear and concise summary:

Text: {text}

Summary:"""

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Generate summary
        response = generate(
            model,
            tokenizer,
            prompt=formatted_prompt,
            verbose=False,
            temp=0.0,
            max_tokens=200  # Limit response length
        )

        # Clean up response by removing control tokens
        cleaned_response = response.split('<|')[0].strip()
        return cleaned_response
    
    except Exception as e:
        raise Exception(f"An error occurred during summarization: {str(e)}")

def main():
    try:
        response = summarize("./data/cargo_cult_science_feynman_1974.txt")
        
        print("\nGenerated Summary:")
        print("-" * 40)
        print(response)
        print("-" * 40)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()