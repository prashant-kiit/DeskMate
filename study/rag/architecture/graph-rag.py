import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# DataBase
catalog = [
    "Nike Running Shoes",
    "Nike Air Max",
    "Nike Basketball Shoes",
    "Adidas Running Shoes",
    "Adidas Sandals",
    "Puma Running Shoes",
]

# Trie Based Index on Tokens of DataBase Records or Vectors
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct"
)

root = TrieNode()

for product in catalog:

    token_ids = tokenizer.encode(
        product,
        add_special_tokens=False
    )

    node = root

    for token_id in token_ids:

        if token_id not in node.children:
            node.children[token_id] = TrieNode()

        node = node.children[token_id]

    node.is_end = True

# traverse to next token in the Trie Based Index on Tokens of DataBase Records or Vectors
def allowed_tokens(generated_product_tokens):

    node = root

    for token_id in generated_product_tokens:

        if token_id not in node.children:
            return []

        node = node.children[token_id]

    return list(node.children.keys())


# Prepare the System Prompt
prompt = """
You are a recommendation system.

User likes:
- running
- sports
- comfortable footwear

Recommend ONE product from the catalog.

Return ONLY the product name.
"""
inputs = tokenizer(prompt, return_tensors="pt")
input_ids = inputs["input_ids"]

# Setup the Model
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct"
)
model.eval()

generated_product_tokens = []

# Model Loop Starts
for _ in range(20):
    # LLM generates Next Token Based on System Prompt
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits[:, -1, :]

    # CONSTRAINED DECODING: Filter in only the allowed tokens from the Original LLM Response Tokens
    allowed_logits = allowed_tokens(
        generated_product_tokens
    )
    if not allowed_logits:
        print("No valid product continuation.")
        break
    mask = torch.full_like(
        logits,
        float("-inf")
    )
    mask[:, allowed_logits] = logits[:, allowed_logits]
    logits = mask

    # Use Allowed Tokens and Prompt Input to generate Next LLM Tokens and Loop Continues
    next_token = torch.argmax(
        logits,
        dim=-1,
        keepdim=True
    )
    token_id = next_token.item()
    generated_product_tokens.append(token_id)
    input_ids = torch.cat(
        [input_ids, next_token],
        dim=1
    )

    # BASE CONDITION: Break the Loop if the all Allowed Tokens in Trie Index is found to be Returned
    node = root
    valid_prefix = True
    for token in generated_product_tokens:
        if token not in node.children:
            valid_prefix = False
            break
        node = node.children[token]
    if valid_prefix and node.is_end:
        break


recommendation = tokenizer.decode(
    generated_product_tokens,
    skip_special_tokens=True
)

print("Recommendation:", recommendation)