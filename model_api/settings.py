# model_api/settings.py

# 🔥 内置常用模型列表
DEFAULT_MODELS = {
    "DeepSeek (深度求索)": [
        "deepseek-chat",
        "deepseek-coder"
    ],
    "Tongyi Qwen (通义千问)": [
        "qwen-max",
        "qwen-plus",
        "qwen-turbo",
        "qwen-long"
    ],
    "Moonshot Kimi (月之暗面)": [
        "moonshot-v1-8k",
        "moonshot-v1-32k",
        "moonshot-v1-128k"
    ],
    "Zhipu GLM (智谱清言)": [
        "glm-4",
        "glm-4-air",
        "glm-4-flash",
        "glm-3-turbo"
    ]
}

MODELS_CONFIG = {
    "DeepSeek (深度求索)": {
        "reg_url": "https://platform.deepseek.com/api_keys",
        "template": {
            "providers": {
                "openai": {
                    "base_url": "https://api.deepseek.com",
                    "apiKey": "{KEY}"
                }
            },
            "agents": {
                "defaults": {
                    "model": "{MODEL}"
                }
            }
        }
    },
    "Tongyi Qwen (通义千问)": {
        "reg_url": "https://dashscope.console.aliyun.com/apiKey",
        "template": {
            "providers": {
                "openai": {
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "apiKey": "{KEY}"
                }
            },
            "agents": {
                "defaults": {
                    "model": "{MODEL}"
                }
            }
        }
    },
    "Moonshot Kimi (月之暗面)": {
        "reg_url": "https://platform.moonshot.cn/console/api-keys",
        "template": {
            "providers": {
                "openai": {
                    "base_url": "https://api.moonshot.cn/v1",
                    "apiKey": "{KEY}"
                }
            },
            "agents": {
                "defaults": {
                    "model": "{MODEL}"
                }
            }
        }
    },
    "Zhipu GLM (智谱清言)": {
        "reg_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "template": {
            "providers": {
                "openai": {
                    "base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "apiKey": "{KEY}"
                }
            },
            "agents": {
                "defaults": {
                    "model": "{MODEL}"
                }
            }
        }
    }
}
