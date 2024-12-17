from mlx_lm import load, generate

# See https://huggingface.co/mlx-community
path_or_hf_repo = "mlx-community/Qwen1.5-7B-Chat-4bit"
model, tokenizer = load(
    path_or_hf_repo, tokenizer_config={"eos_token": "<|im_end|>"}
)

prompt = "Give me a short introduction to large language model."
messages = [
    {
        "role": "system",
        "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    },
    {"role": "user", "content": prompt},
]
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

response = generate(
    model,
    tokenizer,
    prompt=text,
    verbose=True,
    top_p=0.8,
    temp=0.7,
    repetition_penalty=1.05,
    max_tokens=512,
)
