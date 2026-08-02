from transformers import pipeline


class LLMService:
    def __init__(self, model_name:str):
        
        self.pipeline = pipeline("text-generation",
                                 model=model_name
                                 ),
        
    def generate(self,system_prompt:str, user_prompt:str,
                 temperature:float=0, max_tokens:int=256)-> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        output = self.pipeline(messages, temperature=temperature, max_tokens=max_tokens)
        return output[0]["generated_text"][-1]["content"]