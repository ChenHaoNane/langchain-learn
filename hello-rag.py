from dotenv import load_dotenv
load_dotenv()

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# 使用 DeepSeek Chat 模型
model = ChatOpenAI(model="deepseek-chat")

# 使用 HuggingFace 本地中文 embedding 模型
embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-base-zh")

# 构建向量数据库（使用 DocArrayInMemorySearch）
vectorstore = DocArrayInMemorySearch.from_texts(
    ["harrison worked at kensho", "bears like to eat honey"],
    embedding=embedding,
)

retriever = vectorstore.as_retriever()

# 中文提示模板
template = """根据以下上下文回答问题:
{context}

问题: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# 输出处理器
output_parser = StrOutputParser()

# 上下文检索 + 问题传递
setup_and_retrieval = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
)

# 构建 chain
chain = setup_and_retrieval | prompt | model | output_parser

# 测试调用
print(chain.invoke("bears喜欢是哪种食物？"))
