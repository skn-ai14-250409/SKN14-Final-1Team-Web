from dotenv import load_dotenv
import json

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
    아래 제공되는 문서에 없는 내용은 절대 답변에 포함하지 말고, 
    원문 문서 내용과 QA 문서 내용 내에서만 답변 내용을 찾아서 제공하세요. 검색 결과를 논리적으로 조합하여 답변을 구성하세요.
    원문 추가 문서와 QA 추가 문서가 있다면, 해당 내용까지 참고하여 답변을 제공해주세요.
    ### 절대 금지 사항
    - 문서에 **명시되지 않은 내용**은 추론하거나 일반 지식을 가져와서 설명하지 마세요.  
    - 문서에 없는 정보를 '추측', '상식', '추론', '일반 규칙'으로 보충하지 마세요.  
    - 답변에 포함된 모든 사실은 반드시 문서에서 근거를 찾을 수 있어야 합니다.  

    만약 사용자 질문이 구글 api 문서에 대한 질문이 아니라면, 아래 문서는 무시하고 일상 질문에 대해서만 답변하세요.
    일상 질문은 전문적인 내용이 아니고, 코딩과도 관련 없고, 전문지식은 전혀 쓰지 않는 단순한 일상질문입니다.
    
    예를 들어 gitflow가 뭔지 물어보면 답변할 수 없다고 해야 합니다.
    
    원문 문서 : {context_text}
    
    QA 문서 : {context_qa}
    
    원문 추가 문서 : {context_text2}
    
    QA 추가 문서 : {context_qa2}
    
    
    이전 대화 내역 : {history}

    이번 사용자 질문 : {question}
    
    
    추가로, 이번 사용자 질문에 이미지 분석 내용이 들어있고 사용자가 '이미지에 대한 질문을 하거나' 혹은 '이건 어때?' 와 같이 물어보다면 해당 이미지 분석 결과를 참고해서 답변해주세요.
    실제 답변 외에 프롬프트 내용은 답변에 포함시키지 마세요.
    - 만약 이미지 분석 결과가 없거나 관련 없는 질문이라면, 이미지에 대해서는 언급하지 마세요.
    - 금지 답변 예시) 이미지 분석과 관련된 질문이 포함되지 않았으므로, 이미지 분석 결과는 이번 답변에 포함되지 않았습니다.

    """
    )

    basic_chain = basic_prompt | llm | StrOutputParser()

    return basic_chain


def query_setting():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    query_prompt = PromptTemplate.from_template(
        """
       유저의 채팅 히스토리와 현재 질문이 주어집니다. 


       **중요**: 이전 대화 맥락을 반드시 고려해서 질문을 생성하세요.
       - 현재 질문이 이전 대화와 연관되어 있다면, 이전 맥락을 포함한 통합된 질문을 만들어주세요.
       - 동일한 질문을 한글 질문과 영어 질문 2가지 모두 만들어주세요.

       - 예: 바로 전에 "People API 연락처 조회"에 대해 이야기하고 나서, "그럼 프로필 수정은?"이라는 질문이 나오면 "People API에서 프로필 수정 방법"으로 통합해주세요.
       - 주의사항: 이전에 "People API 연락처 조회"에 대해 이야기하고 나서, "Firebase"와 같이 다른 api에 대한 대화 내용이 나온 후 "프로필 수정은?"이라는 질문이 나오면 마지막 대화 맥락에 맞춰서, "Firebase에서 프로필 수정 방법"과 같이 통합해야 합니다.

       - 이전 대화에서 이미 답변이 나온 질문은 생성하지 마세요.
       - 질문은 1개가 될 수도 있고 여러개가 될 수도 있습니다.

       - 만약 사용자 질문에 오타나 잘못된 용어가 포함되어 있다면 올바른 용어로 수정하여 질문을 생성하세요.
        - 예시1 (오타 수정):
            - 사용자 입력: projets.databeses.gte 메서드 쓸때 HTTP 리퀘스트 포맷이 뭐에요?
            - 생성 질문: projects.databases.operations.get 메서드의 HTTP 요청 형식은 무엇인가요?
        - 예시2 (오타 수정):
        - 사용자 입력: ttll이 뭐에요?
        - 생성 질문: TTL(Time-to-Live)이 무엇인가요?

       대화 히스토리: {rewritten}

       JSON 반환 형태:
       {{
           "questions": [
               "맥락을 고려한 통합 질문 1 (한글)",
               "맥락을 고려한 통합 질문 2 (한글)"
               "Integrated question considering context 1 (English)",
               "Integrated question considering context 2 (English)"
               ...
           ]
       }}
       """
    )

    def parse_json(response):
        return json.loads(response.content)  # response.content 사용

    chain = query_prompt | llm | parse_json
    return chain


def classify_chain_setting():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    classification_prompt = PromptTemplate.from_template(
        """
    다음 질문을 분석하여 **주요 목적**에 따라 분류하세요.

    ## 분류 기준
    api: 구글 API 관련 질문이거나, 코딩, 프로그래밍, 보안, 데이터, 네트워킹, IT 기술 등 인터넷 관련 지식에 관한 질문입니다.  
        - 질문에 오타나 알 수 없는 단어가 있더라도, **IT 용어처럼 보이고, 질문 맥락상 기술적인 내용을 묻는 경우에만** `api`로 분류하세요.  
        - 단순히 이해할 수 없는 글자(예: ㅇㄹㄴㄹ, ㅋㅋㅋ, 아무 의미 없는 문자 나열)는 `api`가 아니라 `none`으로 분류하세요.
    basic: 완전 단순한 일상적인 질문 (날씨, 시간, 간단한 대화)
    none: 일상 질문도 아니고, 구글 API나 코딩, 프로그래밍, 인터넷과 전혀 관계 없는 전문적인 지식에 대한 질문

    ## 출력 규칙
    - 오직 다음 중 하나의 단어만 출력: `api`, `basic`, `none`
    - **절대 추가 설명 없이** 해당 단어만 출력
    - 예: `api`

    최근 대화 내용:
    {context}

    이번 사용자 질문:
    {question}

    ## 예시
    질문: 구글 캘린더 API에서 이벤트를 어떻게 추가하나요?  
    정답: api

    질문: Google Drive API로 파일 권한을 수정하는 방법 알려줘  
    정답: api

    질문: Gmail API에서 특정 라벨이 붙은 메일만 가져올 수 있어?  
    정답: api

    질문: 구글 맵 API 호출하는 법 알려주고, 참고로 난 지금 배고파  
    정답: api

    질문: 오늘 날씨 어때?  
    정답: basic

    질문: 지금 몇 시야?  
    정답: basic

    질문: 오늘 날씨 어때? 그리고 딥러닝 CNN 구조 설명해줘  
    정답: none

    질문: 구글 캘린더 API 문서 보여줄 수 있어? 아, 그리고 안녕!  
    정답: api

    질문: 양자컴퓨터에서 큐비트 얽힘이 뭔지 설명해줘  
    정답: none

    질문: 딥러닝에서 Transformer 구조가 뭐야?  
    정답: none

    질문: Docker 컨테이너에서 MySQL 볼륨 마운트 하는 방법 알려줘  
    정답: api

    질문: OpenAI API랑 Google API 차이가 뭐야?  
    정답: api

    질문: AWS S3 SDK 사용법 알려줘  
    정답: api

    질문: Java에서 문자열을 어떻게 뒤집을 수 있나요?  
    정답: api

    질문: 구글 맵 API로 경로 계산하는 방법을 알려줘, 근데 딥러닝을 활용하는 방식으로  
    정답: api

    질문: 'Python'이라는 언어의 특징을 설명해줘  
    정답: none

    질문: 머신러닝에서 과적합을 방지하는 방법은 뭐야?  
    정답: none

    --- 

    질문: {question}  
    정답:
    """
    )

    classify_chain = classification_prompt | llm | StrOutputParser()

    return classify_chain


def simple_chain_setting():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    simple_prompt = PromptTemplate.from_template(
        """
    너는 사용자의 **일상적인 질문**에만 답변하는 도우미야.  

    - 일상적인 질문이면 친절하게 간단히 대답해.  
    - 구글 API 질문이나 전문적인 지식 질문이면 **"대답할 수 없어요."** 라고만 답해야 하는데, 그게 보낸 이미지가 뭔지 물어보는거나 전에 물어본게 뭐였는지 물어보는거면 대답해줘도 돼.
    

    최근 대화 내용:
    {context}

    사용자 질문:
    {question}

    ---

    답변:
    """
    )

    simple_chain = simple_prompt | llm | StrOutputParser()

    return simple_chain


def impossable_chain_setting():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    imp_prompt = PromptTemplate.from_template(
        """
    너는 사용자의 **사용자의 질문**에 대한 내용을 몰라서 답변할 수 없는 챗봇이야.  

    - 최근 대화 내용 및 사용자 질문을 인용해서, **"(사용자가 질문한 내용)은 제가 모르는 내용입니다. 일상 질문 혹은 구글 api 관련 질문만 답변드릴수 있어요"** 라고만 답해.
    (사용자가 질문한 내용)은 그대로 쓰지 말고 요약하여 잘 정제하여 답변할 때 인용하세요.

    최근 대화 내용:
    {context}

    사용자 질문:
    {question}

    ---

    답변:
    """
    )

    imp_chain = imp_prompt | llm | StrOutputParser()

    return imp_chain


def answer_quality_chain_setting_rag():
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    quality_prompt = PromptTemplate.from_template(
        """
        당신은 RAG 기반 답변 평가자입니다.  
        아래는 사용자의 질문과 챗봇의 답변입니다.  
        이 답변이 **검색된 결과**, **사용자의 이전 히스토리**, **이번 질문**에 맞게 적절하게 답변했는지 평가하세요.  

        평가 기준:
        0. 답변에 '죄송하지만', '정보는 제공된 문서에 포함되어 있지 않습니다', '답변할 수 없습니다', '관련된 정보를 찾을 수 없습니다' 와 같이 **부정적, 회피적, 무응답 문구**가 포함되면 무조건 "bad"입니다.  
            - 답변이 사용자의 질문에 대해 아무런 구체적 사실을 제공하지 않고 회피성 멘트만 한다면 무조건 "bad"입니다.  
            - bad 예시 답변: '죄송하지만, GMSMapPoint의 좌표계에서 (0, 0)이 어떤 지점을 의미하는지에 대한 정보는 제공된 문서에 포함되어 있지 않습니다. 다른 질문이 있으시면 말씀해 주세요.'
        1. **검색 결과에 포함되지 않은 정보**를 답변에 포함한 경우, 답변은 "bad"입니다.
        2. **검색 결과와 핵심 내용이 다르게 답변**한 경우, 답변은 "bad"입니다.
        3. **사용자의 히스토리**와 **이번 질문**에 맞지 않는 답변을 한 경우, 답변은 "bad"입니다.
        4. **검색 결과**를 **충실히 반영**하고, **사용자의 과거 질문**이나 **현재 질문**에 맞는 구체적인 답변이 제공되면 "good"입니다.
        5. **검색 결과**를 **무시**하거나 **핵심 내용이 다르게 답변**한 경우, "bad"입니다.

        ---
        사용자의 이전 히스토리: {history}  
        사용자의 이번 질문: {question}

        원문 문서 검색 결과: {context}  
        QA 문서 검색 결과: {context_qa}
        답변: {answer}  
        ---  

        출력은 반드시 "good" 또는 "bad" 중 하나만 하세요.
        """
    )

    return quality_prompt | llm | StrOutputParser()


def alternative_queries_chain_setting():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    alt_prompt = PromptTemplate.from_template(
        """
        당신은 구글 api 문서에 대한 전문가이고, 당신이 아는 api 주제는 아래 11가지입니다.
        
        "map": "Google Maps API (구글 맵 API)",
        "firestore": "Google Firestore API (구글 파이어스토어 API)",
        "drive": "Google Drive API (구글 드라이브 API)",
        "firebase_authentication": "Google Firebase API (구글 파이어베이스 API)",
        "gmail": "Gmail API (구글 메일 API)",
        "google_identity": "Google Identity API (구글 인증 API)",
        "calendar": "Google Calendar API (구글 캘린더 API)",
        "bigquery": "Google BigQuery API (구글 빅쿼리 API)",
        "sheets": "Google Sheets API (구글 시트 API)",
        "people": "Google People API (구글 피플 API)",
        "youtube": "YouTube API (구글 유튜브 API)"
        
        사용자의 이전 대화 내역과 이번 질문의 맥락을 고려하여,
        당신이 아는 내용을 최대한 활용해서 각 답변 당 2~3문장 내로 구체적으로 자세히 답변해주세요.
        다른 방안을 제시하지 말고, 반드시 사용자의 질문 요구를 충족하는 답변을 생성하세요.

        답변은 동일한 내용을 영어와 한글 각각 1개씩 만들어주세요.
    
        사용자의 이전 히스토리:
        {history}

        사용자의 이번 질문:
        {question}

        ---
        JSON 반환 형태:
       {{
           "docs": [
               "한글 답변",
               "english answer"
           ]
       }}
        """
    )

    def parse_json(response):
        try:
            return json.loads(response.content)
        except Exception:
            # LLM이 JSON 형식을 지키지 못했을 때 빈 리스트 반환
            return {"questions": []}

    chain = alt_prompt | llm | parse_json
    return chain