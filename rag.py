import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 使用 WebBaseLoader 从网页加载内容，并仅保留标题、标题头和文章内容
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()

# 检查加载的文档内容长度
print(len(docs[0].page_content))  # 打印第一个文档内容的长度

# 使用 RecursiveCharacterTextSplitter 将文档分割成块，每块1000字符，重叠200字符
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

# 检查分割后的块数量和内容
print(len(all_splits))  # 打印分割后的文档块数量

print(len(all_splits[0].page_content))  # 打印第一个块的字符数

print(all_splits[0].page_content)  # 打印第一个块的内容

print(all_splits[1].page_content)  # 打印第一个块的内容


embedding = HuggingFaceEmbeddings(model_name="intfloat/e5-base")
# 使用 Chroma 向量存储和 HuggingFaceEmbeddings 模型，将分割的文档块嵌入并存储
vectorstore = Chroma.from_documents(
    documents=all_splits,
    embedding=embedding
)

# 查看 vectorstore 数据类型
print(type(vectorstore))

# 使用 VectorStoreRetriever 从向量存储中检索与查询最相关的文档
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

# 查看 retriever 数据类型
print(type(retriever))

# 使用 retriever 检索与查询最相关的文档
retrieved_docs = retriever.invoke("What are the approaches to Task Decomposition?")

# 检查检索到的文档内容
print(len(retrieved_docs))  # 打印检索到的文档数量

for doc in retrieved_docs:
    print(doc.page_content)
    print("-" * 100)

llm = ChatOpenAI(model="deepseek-chat")

prompt = hub.pull("rlm/rag-prompt")

# 打印模板
print(prompt.messages)

# 定义格式化文档的函数
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 使用 LCEL 构建 RAG Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 流式生成回答
for chunk in rag_chain.stream("What is Task Decomposition?"):
    print(chunk, end="", flush=True)

# 流式生成回答
for chunk in rag_chain.stream("What is ToT?"):
    print(chunk, end="", flush=True)