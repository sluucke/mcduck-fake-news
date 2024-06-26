from abc import ABC, abstractmethod
import requests
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import llm
from langchain_community.document_loaders.csv_loader import CSVLoader
import pandas as pd


load_dotenv()

# Estrutural: Fachada
class LLM:
    def prompt(self, message: str, llm: object) -> str:
        if isinstance(llm, ChatGPT):
            return llm.chat_prompt(message)
        else:
            return "No LLM found"


# Criacional: singleton
class ChatGPT:
    llm = None

    def __init__(self):
        if ChatGPT.llm is None:
            __conn = ChatOpenAI(
                temperature=1, model='gpt-4o')
            ChatGPT.llm = __conn

    def chat_prompt(self, prompt: object, data: str, afirmacao: str) -> str:
        return llm.LLMChain(llm=ChatGPT.llm, prompt=prompt).run(
            data=data, afirmacao=afirmacao)
    
    def get_instance(self):
        return ChatGPT.llm

# Comportamental: Template Method


class Parser(ABC):
    def chat_prompt(self, query: str):
        data = self.get_data(query)
        self.generate_csv_data(data)
        docs = self.parse_llm(query)
        prompt = self.prompt_maker()

        return {
            'prompt': prompt,
            'docs': docs,
        }

    @abstractmethod
    def get_data():
        pass

    @abstractmethod
    def generate_csv_data(self):
        pass

    @abstractmethod
    def parse_llm(self):
        pass

    @abstractmethod
    def prompt_maker(self):
        pass


class IBGEParser(Parser):
    def __init__(self):
        self.url = "http://servicodados.ibge.gov.br/api/v3/noticias/?q="

    def get_data(self, query: str):
        response = requests.get(self.url + query + "&qtd=1000")
        data = response.json()
        return data

    def generate_csv_data(self, data: dict) -> map:
        # data = self.get_data(query)

        formattedData = map(
            lambda x: {
                "id": x['id'],
                "title": x['titulo'],
                "introducao": x['introducao'],
                "link": x['link']
            }, data['items'])

        df = pd.DataFrame(formattedData)

        df.to_csv('output.csv', index=False, encoding='utf8')

    def parse_llm(self, query: str):
        loader = CSVLoader(file_path='./output.csv', encoding='utf8')
        docs = loader.load()
        embeddings = OpenAIEmbeddings()

        db = FAISS.from_documents(docs, embeddings)

        similar = db.similarity_search(query=query, k=10)

        return [doc.page_content for doc in similar]

    def prompt_maker(self):
        prompt_model = '''
        Você é um verificador de fake news, dado a base de dados abaixo, determine se a afirmação é verdadeira ou falsa.
        Siga as instruções abaixo:
        1/ Seja objetivo e claro
        2/ Não use palavras ofensivas
        3/ Justifique sua resposta com base na base de dados fornecida
        4/ Coloque o link das notícias que você usou para justificar sua resposta
        5/ Utilize alguns conectivos que são sons de pato para deixar a conversa mais divertida. Como por exemplo: "quack", "quack quack", "quack quack quack"
        6/ Retorne um script HTML com a resposta utilizando tailwindcss
        7/ Retorne apenas o código HTML da resposta, sem nenhum outro texto
        8/ Não utilize a tag html, body ou head, apenas o conteúdo interno
        9/ Aqui está um modelo de resposta: <div class="text-white p-4"><p class="text-lg text-white">Olá, quack quack!</p><p>RESPOSTA....</p><p>Fontes:</p><ul>...</ul></div>
        
        Aqui está a base de dados:
        {data}
       
        Aqui está a afirmação do usuário:
        {afirmacao}
        
        
        Responda com base neste modelo:
        Olá, quack quack!
        
        
        Escreva sua resposta: 
        '''

        prompt = PromptTemplate(
            input_variables=["data", "afirmacao"],
            template=prompt_model
        )

        return prompt




class Proxy:
    def check_similar_query(self, query: str, searchs: object) -> object | None:
        chatGPT = ChatGPT()
        
        # ChatGPT.
        prompt = self.prompt_maker()
        
        content = chatGPT.chat_prompt(prompt, searchs, query)

        return content

    def prompt_maker(self):
        prompt = '''
        Você é um veificador de similaridade, dado a base abaixo, determine o id da notícia mais similar a afirmação do usuário.
        1\ Se a afirmação do usuário não for encontrada na base, retorne -1
        2\ Retorne apenas o id da notícia mais similar, sem nenhum outro texto

        Aqui está a base de dados:
        {data}

        Aqui está a afirmação do usuário:
        {afirmacao}

        Escreva sua resposta:
        '''

        prompt = PromptTemplate(
            input_variables=["data", "afirmacao"],
            template=prompt
        )

        return prompt
    




# print(Proxy().check_similar_query("O PIB do Brasil cresceu em 2020"))
