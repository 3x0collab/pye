# from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain.docstore.document as docstore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
import os
from dotenv import load_dotenv
import re

load_dotenv()



class VortexIngester:

    def __init__(self, data_text: str,collection_name:str):
        self.data_text = data_text
        self.collection_name = self.clean_str(collection_name)
        self.persist_directory = "./data/chroma"

    def clean_str(self,string):
        pattern = re.compile(r'\s+')
        return re.sub(pattern, '', string)



    def ingest(self) -> None:
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = 1000,
            chunk_overlap  = 0,
            length_function = len,
        )

        texts = text_splitter.create_documents([self.data_text]) 

        embeddings = OpenAIEmbeddings(client=None, openai_api_key=os.getenv('OPENAI_API_KEY') )
        logger.info("Loading embeddings")
        vector_store = Chroma.from_documents(
            texts,
            embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
        )

        logger.info("Created Chroma vector store")
        vector_store.persist()
        logger.info("Persisted Chroma vector store")
