from pydantic import BaseSettings


class Environment(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    class Config:
        env_file = ".env"  # Path to .env file


env = Environment()
