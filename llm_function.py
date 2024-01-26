from openai import OpenAI
from dotenv import load_dotenv
import os
from llama_cpp import Llama
import parameters
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from llama_index.llms import LlamaCPP
from llama_index.llms.vllm import Vllm
'''
import lmformatenforcer
from llama_index.prompts.lmformatenforcer_utils import (
    activate_lm_format_enforcer,
    build_lm_format_enforcer_function,
)
from llama_index.llms import LlamaCPP
'''
def get_llm():
    # llama-cpp
    if parameters.llm_method == 'llama-cpp':
        llm = Llama(model_path = parameters.model_path, n_ctx = parameters.n_ctx, n_gpu_layers = parameters.n_gpu_layers)

    # openai
    elif parameters.llm_method == 'openai':
        load_dotenv()
        llm = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY"),
        ) #api_key = os.getenv("OPENAI_API_KEY"),
    
    # llama_index (llama-cpp)
    elif parameters.llm_method == 'llama-index':
        llm = LlamaCPP(
            model_path = parameters.model_path,
            temperature = parameters.temperature,
            max_new_tokens = parameters.max_tokens,
            context_window = parameters.n_ctx,
            generate_kwargs={},
            model_kwargs={"n_gpu_layers": parameters.n_gpu_layers},
            verbose = True,
        )
    
    #vllm
    elif parameters.llm_method == 'vllm':
        llm = Vllm( # Variable Language Model 各種參數
            model = "WizardLM/WizardMath-13B-V1.0", # 使用了名稱為 "WizardLM/WizardMath-13B-V1.0" 的預訓練語言模型
            dtype = "float16", # 指定模型的數據類型為 float16，即半精度浮點數
            tensor_parallel_size = 1, # 指定張量並行的大小為 1，表示不使用張量並行
            temperature = parameters.temperature, #溫度即隨機性
            max_new_tokens = parameters.max_tokens, #最大 token 數
            vllm_kwargs={
                "swap_space": 1, # 指定交換空間的大小為 1
                "gpu_memory_utilization": 0.7, # 指定GPU內存利用率為 0.7
                "max_model_len": parameters.n_ctx, # 使用了程式中定義的 parameters.n_ctx 作為模型的最大上下文長度
            },
        )
    
    return llm


def call_llm(llm, question, pattern_format = None):
    # llama-cpp
    if parameters.llm_method == 'llama-cpp':
        response = llm(
                question,
                max_tokens = parameters.max_tokens,
            )
        output = response['choices'][0]['text']
    
    # openai
    elif parameters.llm_method == 'openai':
        response = llm.chat.completions.create(
            # 使用 chat 模式生成對話
            #model = 'gpt-4-0613',
            model = 'gpt-3.5-turbo-1106',
            temperature = parameters.temperature,
            messages = [
                {
                    'role': 'user', # 設定角色為使用者
                    'content': question, # 使用者的對話內容
                }
            ]
        )
        output = response.choices[0].message.content # 取得模型生成的回應
    
    # llama_index
    elif parameters.llm_method == 'llama-index':
        regex_parser = lmformatenforcer.RegexParser(pattern_format)
        lm_format_enforcer_fn = build_lm_format_enforcer_function(llm, regex_parser)
        with activate_lm_format_enforcer(llm, lm_format_enforcer_fn):
            response = llm.complete(question)
        output = response.text
    

    #vllm
    elif parameters.llm_method == 'vllm':
        output = llm.complete(question).text
    
    return output
    
