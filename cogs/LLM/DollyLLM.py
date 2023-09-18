# https://huggingface.co/databricks/dolly-v2-3b
# pip install "accelerate>=0.16.0,<1" "transformers[torch]>=4.28.1,<5" "torch>=1.13.1,<2"

import torch
from transformers import pipeline

generate_text = pipeline(model="databricks/dolly-v2-3b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")

def prompt(input):
    res = generate_text(str(input))
    return (res[0]["generated_text"])


from pathlib import Path
import sys

#path_root = Path(__file__).parents[2]
sys.path.append(str(r"C:\Users\Alexa\OneDrive - Emory University\Desktop\RProjects\Learning\Learning\SomeYellows\LLM\DollyLLM.py"))
print(sys.path)