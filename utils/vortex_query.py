from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import AIMessage, HumanMessage,SystemMessage
from langchain.vectorstores.chroma import Chroma
import json

# from settings import COLLECTION_NAME, PERSIST_DIRECTORY
import re

from langchain.prompts import HumanMessagePromptTemplate,SystemMessagePromptTemplate,ChatPromptTemplate

class ChatHistoryEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, HumanMessage) or isinstance(obj, AIMessage):
			return obj.__dict__
		return super().default(obj)



def serialize_chat_history(chat_history,user):
	serialized_history = []
	print('serios',user)
	for message in chat_history:
		if isinstance(message, HumanMessage):
			serialized_message = {
				"type": "HumanMessage",
				"content": message.content,
				"user":user
			}
		elif isinstance(message, AIMessage):
			serialized_message = {
				"type": "AIMessage",
				"content": message.content,
				"user":user
			}
		serialized_history.append(serialized_message)
	return json.dumps(serialized_history)

def deserialize_chat_history(serialized_chat_history,user):
	chat_history_data = json.loads(serialized_chat_history)
	chat_history = []
	for entry in chat_history_data:
		if entry.get('user') == user:
			if entry["type"] == "HumanMessage":
				chat_history.append(HumanMessage(content=entry["content"]))
			elif entry["type"] == "AIMessage":
				chat_history.append(AIMessage(content=entry["content"]))
	return chat_history






class VortexQuery:
	def __init__(self,collection,prompt="Am a Personal AI assistant",user=None,save_history=True):
		load_dotenv()
		self.collection = collection
		self.connector = self.collection.connector if hasattr(self.collection,'connector') else self.collection.connection.connector
		if save_history:
			self.chat_history =  deserialize_chat_history(self.collection.chat_history or '[]',user)
		else:
			self.chat_history =  []
		self.collection_name = self.clean_str(f"{self.connector.name}_{str(self.connector.created_by)}" )
		self.persist_directory = "./data/chroma"
		self.prompt = prompt
		self.chain = self.make_chain()
		self.user = user
		self.save_history = save_history
		print('dhhresd')






	def clean_str(self,string):
		pattern = re.compile(r'\s+')
		return re.sub(pattern, '', string)

	def make_chain(self):

		# custom_prompt = PromptTemplate(
		#     template="{prompt}",
		#     input_variables=["prompt"]  
		# )
		# custom_prompt.format(prompt=self.prompt)

		general_system_template = self.prompt + """ 
		 
				---------
				{context}
				----------
			"""

		general_user_template = "Question:```{question}```"

		messages = [
            SystemMessagePromptTemplate.from_template(general_system_template),
            HumanMessagePromptTemplate.from_template(general_user_template)
		]

		qa_prompt = ChatPromptTemplate.from_messages( messages )


		model = ChatOpenAI(
			client=None,
			model="gpt-3.5-turbo",
			temperature=0,
		) 

		embedding = OpenAIEmbeddings(client=None)

		vector_store = Chroma(
			collection_name=self.collection_name,
			embedding_function=embedding,
			persist_directory=self.persist_directory ,
		)

		chain = ConversationalRetrievalChain.from_llm(
			model,
			retriever=vector_store.as_retriever(),
			chain_type="stuff",
			combine_docs_chain_kwargs={'prompt': qa_prompt}

			)
		# if self.prompt:
		# 	self.chat_history.append(SystemMessage(content=self.prompt))

		return chain

	def ask_question(self, question=""):
		if question:
			if self.prompt:
				question_pr = f"""
Question: {question}.

You are provided with text delimited by four quotes as your task:  ````{self.prompt}.````
				"""
			else:
				question_pr = question
			response = self.chain({"question": question_pr, "chat_history": self.chat_history})

			answer = response["answer"]
			source = "" #response["source_documents"]

			if self.save_history:
				self.chat_history.append(HumanMessage(content=question))
				self.chat_history.append(AIMessage(content=answer))

				self.collection.chat_history = serialize_chat_history(self.chat_history,self.user)
				self.collection.save() 

			return answer
