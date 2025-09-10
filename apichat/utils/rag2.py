from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# LangChain OpenAI
from langchain_openai import ChatOpenAI

load_dotenv()


def basic_chain_setting():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    basic_prompt = PromptTemplate.from_template(
        """
    당신은 api 문서 관련 전문 챗봇으로서 사용자의 질문에 정확하고 친절하게 답변해야 합니다.
    아래 제공되는 문서에 없는 내용은 절대 답변에 포함하지 말고, 문서 내에서만 답변 내용을 찾아서 제공하세요.
    만약 사용자 질문이 구글 api 문서에 대한 질문이 아니라면, 아래 문서는 무시하고 일상 질문에 대해서만 답변하세요.
    일상 질문은 전문적인 내용이 아니고, 코딩과도 관련 없고, 전문지식은 전혀 쓰지 않는 단순한 일상질문입니다.
    
    예를 들어 gitflow가 뭔지 물어보면 답변할 수 없다고 해야 합니다.
    
    문서 : {context}
    
    이전 대화 내역 : {history}

    이번 사용자 질문 : {question}
    """
    )

    basic_chain = basic_prompt | llm | StrOutputParser()

    return basic_chain
