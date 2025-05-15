from dotenv import load_dotenv
load_dotenv()

from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

planner = (
    ChatPromptTemplate.from_template("生成关于以下内容的论点：{topic}")
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
    | { "base_response": RunnablePassthrough()}
)

# 创建正面论证的处理链
positive_chain = (
    ChatPromptTemplate.from_template("生成关于以下内容的正面论证：{base_response}")
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

# 创建反面论证的处理链
negative_chain = (
    ChatPromptTemplate.from_template("生成关于以下内容的反面论证：{base_response}")
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

final_responder = (
    ChatPromptTemplate.from_messages([
        ('ai', '{original_response}'),
        ('human', '正面观点：\n{positive}\n\n反面观点：\n{negative}'),
        ('system', '给出批评后生成最终回应'),
    ])
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

chain = (
    planner
    | {
        "positive": positive_chain,
        "negative": negative_chain,
        "original_response": itemgetter("base_response")
    }
    | final_responder
)


for chunk in chain.stream({"topic": "是否应该使用 langchain 进行 RAG 开发"}):
    print(chunk, end="", flush=True)


