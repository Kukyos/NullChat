"""
Local LLM service using HuggingFace transformers (Llama 3 8B Instruct) - GPU Optimized
"""
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
import torch
import logging
from ..data.college_data import COLLEGE_INFO

# MAXIMUM POWER SETTINGS
torch.cuda.empty_cache()  # Clear any existing GPU memory
torch.backends.cudnn.benchmark = True  # Optimize for consistent input sizes
torch.backends.cuda.matmul.allow_tf32 = True  # Use TF32 for faster matmul on RTX cards
torch.backends.cudnn.allow_tf32 = True  # Use TF32 for convolutions

logger = logging.getLogger(__name__)

class LocalLLMService:
    def __init__(self):
        # FULL POWER MODE - Llama 3 8B with maximum resource usage!
        model_id = "meta-llama/Meta-Llama-3-8B-Instruct"  
        logger.info(f"🚀 LOADING FULL POWER MODEL: {model_id}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # UNLEASH MAXIMUM POWER - Use ALL available resources!
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",  # Automatically use all available devices
            trust_remote_code=True,
            attn_implementation="eager",
            low_cpu_mem_usage=False,  # Use ALL CPU memory available
            # No memory limits - use the full 8GB VRAM and all system RAM!
        )
        
        # MAXIMUM POWER PIPELINE - No holds barred!
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=512,  # Maximum tokens for detailed responses
            temperature=0.7,
            do_sample=True,
            return_full_text=False,
            pad_token_id=self.tokenizer.eos_token_id,
            batch_size=1,  # Optimize for single requests
            # Use full compute power!
        )

    def generate_response(self, question: str, context: str = "") -> dict:
        # Create a comprehensive prompt with college data
        system_msg = f"""You are a helpful college chatbot for State Institute of Technology. Use the following information to answer student questions accurately and helpfully. Keep responses concise but informative.

COLLEGE INFORMATION:
{COLLEGE_INFO}

Answer the student's question based on the above information. If the question is in Hindi/mixed language, respond in the same style."""
        
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_msg}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
        
        logger.info(f"Generating response for: {question}")
        try:
            outputs = self.generator(prompt)
            response_text = outputs[0]["generated_text"]
            
            return {
                "answer": response_text.strip(),
                "confidence": 0.8,
                "source": "llama3-local"
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "answer": f"I'm having trouble processing your request: {str(e)}",
                "confidence": 0.1,
                "source": "error"
            }

# Global instance
local_llm_service = LocalLLMService()
