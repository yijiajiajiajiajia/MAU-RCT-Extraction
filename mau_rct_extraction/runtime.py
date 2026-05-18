import time

import requests

client = None
model_name = None


def configure_runtime(openai_client, selected_model_name):
    global client, model_name
    client = openai_client
    model_name = selected_model_name


# ----------------------------
# 带重试机制的 API 调用函数
# ----------------------------
def call_api_with_retry(messages, max_retries=3, initial_delay=2):
    """带重试机制的 API 调用"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0,
                timeout=120.0
            )
            return response
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                Exception) as e:
            if attempt == max_retries - 1:  # 最后一次重试
                raise e
            delay = initial_delay * (2 ** attempt)  # 指数退避
            print(f"API调用失败，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay)
    return None
