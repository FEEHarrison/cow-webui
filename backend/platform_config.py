class PlatformConfig:
    PLATFORMS = {
        'openai': {
            'api_keys': ['OPEN_AI_API_KEY', 'OPEN_AI_API_BASE'],
            'env_vars': {
                'OPEN_AI_API_KEY': '',
                'OPEN_AI_API_BASE': ''
            }
        },
        'zhipuai': {
            'api_keys': ['ZHIPU_AI_API_KEY', 'ZHIPU_AI_API_BASE'],
            'env_vars': {
                'ZHIPU_AI_API_KEY': '',
                'ZHIPU_AI_API_BASE': ''
            }
        },
        'azure': {
            'api_keys': ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_API_BASE'],
            'env_vars': {
                'AZURE_OPENAI_API_KEY': '',
                'AZURE_OPENAI_API_BASE': ''
            }
        },
        'tencent': {
            'api_keys': ['TENCENT_API_KEY', 'TENCENT_API_BASE'],
            'env_vars': {
                'TENCENT_API_KEY': '',
                'TENCENT_API_BASE': ''
            }
        }
    }

    @classmethod
    def get_platform_api_keys(cls, platform):
        return set(cls.PLATFORMS.get(platform, {}).get('api_keys', []))
    @classmethod
    def get_platform_env_vars(cls, platform, config_data):
        env_vars = cls.PLATFORMS.get(platform, {}).get('env_vars', {}).copy()
        for key in env_vars:
            config_key = key.upper()
            if config_key in config_data:
                env_vars[key] = config_data[config_key]
        return env_vars

    @classmethod
    def is_valid_platform(cls, platform):
        return platform in cls.PLATFORMS

    @classmethod
    def get_all_platforms(cls):
        return list(cls.PLATFORMS.keys())