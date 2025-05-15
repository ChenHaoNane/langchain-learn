from dotenv import load_dotenv
load_dotenv()

from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableMap

planner = (
    ChatPromptTemplate.from_template('生成关于{feture}功能的需求分析')
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
    | { "base_response": RunnablePassthrough() }
)

python_code_chain = (
    ChatPromptTemplate.from_template('生成关于{base_response}的python代码')
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

nodejs_code_chain = (
    ChatPromptTemplate.from_template('生成关于{base_response}的nodejs代码')
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

final_responder = (
    ChatPromptTemplate.from_messages([
        ('ai', '{original_response}'),
        ('human', 'python代码：\n{python_code}\n\nodejs\n{nodejs_code}'),
        ('system', '给出代码后，生成代码注释'),
    ])
    | ChatOpenAI(model="deepseek-chat")
    | StrOutputParser()
)

chain = (
    planner
    | 
    {
        "python_code": python_code_chain,
        "nodejs_code": nodejs_code_chain,
        "original_response": itemgetter("base_response")
    }
    | final_responder
)

for chunk in chain.stream({"feture": "用户登录"}):
    print(chunk, end="", flush=True)

