from pydantic import BaseSettings


# enviroment variables
class Environment(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"  # Path to .env file


env = Environment()
