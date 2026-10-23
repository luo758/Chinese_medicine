import os
from dotenv import load_dotenv

from common.path_utils import get_file_path

# load_dotenv()
load_dotenv(get_file_path(".env"))


class Config:
    def __init__(self):
        # 大模型相关
        self.MODEL_API_KEY = os.getenv("MODEL_API_KEY")
        self.MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
        self.MODEL_NAME = os.getenv("MODEL_NAME")

        # neo4j相关
        self.NEO4J_URI = os.getenv("NEO4J_URI")
        self.NEO4J_USER = os.getenv("NEO4J_USER")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

        # embedding模型
        # self.EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH")


if __name__ == "__main__":
    conf = Config()
    print(conf.MODEL_NAME)