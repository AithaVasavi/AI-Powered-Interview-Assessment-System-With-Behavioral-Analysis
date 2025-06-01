import json
import os

class ModelManager:
    def __init__(self, config_file="model_config.json"):
        self.config_file = config_file
        self.default_config = {
            'models': {
                'deepseek-r1:7b': {
                    'name': 'DeepSeek R1 7B',
                    'description': 'Balanced model for general interview scenarios',
                    'system_prompt': """You are an AI interviewer. Assess candidate responses professionally 
                    and provide constructive feedback. Focus on both technical accuracy and communication skills.""",
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                'llama2:13b': {
                    'name': 'Llama 2 13B',
                    'description': 'More comprehensive for technical interviews',
                    'system_prompt': """You are an expert technical interviewer. Focus on deep technical knowledge,
                    problem-solving ability, and coding skills. Provide detailed feedback on technical accuracy.""",
                    'temperature': 0.8,
                    'max_tokens': 1500
                },
                'mistral:7b': {
                    'name': 'Mistral 7B',
                    'description': 'Specialized for behavioral interviews',
                    'system_prompt': """You are a behavioral interview specialist. Focus on assessing soft skills,
                    communication ability, and cultural fit. Provide nuanced feedback on behavioral aspects.""",
                    'temperature': 0.6,
                    'max_tokens': 1000
                }
            },
            'custom_prompts': {}
        }
        self.load_config()
    
    def load_config(self):
        """Load model configuration from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_model_config(self, model_name):
        """Get configuration for a specific model"""
        return self.config['models'].get(model_name)
    
    def list_models(self):
        """List all available models"""
        return [(model_id, config['name'], config['description']) 
                for model_id, config in self.config['models'].items()]
    
    def add_custom_prompt(self, name, prompt_template):
        """Add a custom prompt template"""
        self.config['custom_prompts'][name] = prompt_template
        self.save_config()
    
    def get_custom_prompt(self, name):
        """Get a custom prompt template"""
        return self.config['custom_prompts'].get(name)
    
    def list_custom_prompts(self):
        """List all custom prompt templates"""
        return list(self.config['custom_prompts'].keys())
    
    def remove_custom_prompt(self, name):
        """Remove a custom prompt template"""
        if name in self.config['custom_prompts']:
            del self.config['custom_prompts'][name]
            self.save_config()
    
    def update_model_config(self, model_name, updates):
        """Update configuration for a specific model"""
        if model_name in self.config['models']:
            self.config['models'][model_name].update(updates)
            self.save_config()
    
    def get_formatted_prompt(self, model_name, custom_prompt_name=None, **kwargs):
        """Get formatted prompt for a model, optionally using a custom template"""
        model_config = self.get_model_config(model_name)
        if not model_config:
            raise ValueError(f"Model {model_name} not found")
        
        if custom_prompt_name:
            prompt_template = self.get_custom_prompt(custom_prompt_name)
            if not prompt_template:
                raise ValueError(f"Custom prompt {custom_prompt_name} not found")
        else:
            prompt_template = model_config['system_prompt']
        
        return prompt_template.format(**kwargs)