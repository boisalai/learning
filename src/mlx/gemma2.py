from mlx_lm import load, generate

model, tokenizer = load("mlx-community/gemma-2-9b-8bit")
# model, tokenizer = load("mlx-community/gemma-2-27b-4bit")
response = generate(model, tokenizer, prompt="hello", verbose=True)

