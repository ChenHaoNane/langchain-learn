from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap, RunnableLambda


system_template = "讲一个关于{topic}的故事"

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template),
])

llm = ChatOpenAI(model="deepseek-chat")

# messages = [
#     SystemMessage(content="Translate the following from English into Chinese"),
#     HumanMessage(content="hi!"),
# ]

parser = StrOutputParser()

chain = prompt_template | llm | parser

response = chain.invoke({"topic": "猫"})

print(response)

