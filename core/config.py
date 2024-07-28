from pydantic_settings import BaseSettings


class Config(BaseSettings):
    exec_name: str = "Hearthstone.exe"
    new_rule_name: str = "BlockHearthstoneTemp"
    sleep_interval: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config_instance = Config()
