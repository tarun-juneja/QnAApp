import re
import os
import fitz
# import anthropic
# from langchain_together import ChatTogether
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_fireworks import Fireworks
# from langchain_groq import ChatGroq
from langchain_cohere import ChatCohere
from langchain_core.prompts import PromptTemplate
from gtts import gTTS
import time
import os

# from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
# from datasets import load_dataset
# import torch
# import soundfile as sf
# from langchain_community.document_loaders import PyMuPDFLoader

class generator_llm:
    def __init__(self, file) -> None:
        # self.llm = Fireworks(
        #     api_key=os.getenv("FIREWORKS_API_KEY"),
        #     model=os.getenv("FIREWORKS_MODEL"),
        #     top_p=1.0,
        #     temperature=0.5,
        #     max_tokens=3000, seed=42)
        self.llm=ChatCohere(cohere_api_key=os.getenv("COHERE_API_KEY"), max_tokens=None, model='command-r-plus', temperature=0.5, seed=444)
        # self.llm=ChatGroq(temperature=0.5, model="llama3-groq-70b-8192-tool-use-preview", api_key=os.getenv("GROQ_API_KEY"), seed=4012)
        self.file = file
        pdf_bytes = self.file.getvalue()
        self.documents = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.__input_content = ""
        for page in self.documents:
            self.__input_content += re.sub(" {2,}", ' ', re.sub("\n \n{1,}", ' ', page.get_text().strip()))
        input_template = """{question}
        
        Context:
        ------ 
        {context}
        ------"""
        self.__prompt = PromptTemplate.from_template(input_template)
    
    def __query_formatter(self, num_qs, btl, detail):
        if detail.lower()=="short":
            detail_level = "All the answers should be short, precise and at max 4 sentences long."
        elif detail.lower()=="detailed":
            detail_level = "All the answers to questions should be well explained in detail with more than 10 sentences but should not be exhaustive."
        elif detail.lower()=="medium":
            detail_level="All the Answers to questions should be explained. The response length should be between 5 to 8 sentences."

        template = """Generate exactly {number_of_questions} descriptive question and answer pairs that are based on the context provided below. 
        Ensure each generated question and answer pair is different from the other generated pair, in terms of the topics/aspects/concepts the question covers. The {number_of_questions} pair of question and answer must consist of exactly {level1} pair of question and answer addressing Bloom's Taxonomy Level 1 which is Recall capability, {level2} pair of question and answer addressing Bloom's Taxonomy Level 2 which is Understanding of Concept, {level3} pair of question and answer addressing Bloom's Taxonomy Level 3 which is Application of Concept and {level4} pair of question and answer addressing Bloom's Taxonomy Level 4 which is using concept for Analysis of situation.
        {detail_level}
        If the new question and answer pairs satisfy all the above conditions then structure the final output as a json array of object (and only a json array of objects), where each object comprises of the following keys whose definitions are provided below:
        "question": the value is the text for the generated question,
        "answer": the value is the text for the generated answer,
        "addressed_BTL": the bloom's taxonomy level that the question answer pair is related to.
        DO NOT generate or add ```json or any output that is not part of actual output."""
        input_prompt = PromptTemplate.from_template(template=template)
        return input_prompt.format(number_of_questions=num_qs, level1=btl[1], level2=btl[2],level3=btl[3],level4=btl[4], detail_level=detail_level)
        
        
    def get_qna(self, num_qs, btl, detail_level):
        # if detail.lower()=="short":
        #     detail_level = "All the answers should be short, precise and at max 4 sentences long."
        # elif detail.lower()=="detailed":
        #     detail_level = "All the answers to questions should be well explained in detail with more than 10 sentences but should not be exhaustive."
        # elif detail.lower()=="medium":
        #     detail_level="All the Answers to questions should be explained. The response length should be between 5 to 8 sentences."

        # template = """Generate exactly {number_of_questions} descriptive question and answer pairs that are based on the context provided below. 
        # Ensure each generated question and answer pair is different from the other generated pair, in terms of the topics/aspects/concepts the question covers. The {number_of_questions} pair of question and answer must consist of exactly {level1} pair of question and answer addressing Bloom's Taxonomy Level 1 which is Recall capability, {level2} pair of question and answer addressing Bloom's Taxonomy Level 2 which is Understanding of Concept, {level3} pair of question and answer addressing Bloom's Taxonomy Level 3 which is Application of Concept and {level4} pair of question and answer addressing Bloom's Taxonomy Level 4 which is using concept for Analysis of situation.
        # {detail_level}
        # If the new question and answer pairs satisfy all the above conditions then structure the final output as a json array of object (and only a json array of objects), where each object comprises of the following keys whose definitions are provided below:
        # "question": the value is the text for the generated question,
        # "answer": the value is the text for the generated answer,
        # "addressed_BTL": the bloom's taxonomy level that the question answer pair is related to.
        # DO NOT generate any output or statements that is not part of json output."""
        # input_prompt = PromptTemplate.from_template(template=template)
        # question = input_prompt.format(number_of_questions=num_qs, level1=btl[1], level2=btl[2],level3=btl[3],level4=btl[4], detail_level=detail_level)
        question = self.__query_formatter(num_qs, btl, detail_level)
        query = self.__prompt.format(question=question, context=self.__input_content)

        response = self.llm.invoke(query)
        return response.content.replace("```json", "").replace("```", "")

    def get_audio(self):
        template = """
        You are a subject matter expert in Finance domain and a podcaster. You are planning for a podcast based on content provided. You need to create a script for podcast that is engaging and explains the concepts in the content in 3-5 minutes without making it too dry and technical. Where ever possible include simple examples and references to explain the concepts. DO NOT include any additional text like "Here is a podcast script".
        """
        input_prompt = PromptTemplate.from_template(template=template)
        question = input_prompt.format()
        # question = self.__query_formatter(num_qs, btl, detail_level)
        query = self.__prompt.format(question=question, context=self.__input_content)

        response = self.llm.invoke(["human",query])
        # processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        # model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        # vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

        # inputs = processor(text=response.content, return_tensors="pt")

        # # load xvector containing speaker's voice characteristics from a dataset
        # embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        # speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

        # speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

        # sf.write("speech.wav", speech.numpy(), samplerate=16000)
        
        tts = gTTS(response.content, lang='en', tld='co.in')
        filename = f'./{self.file.name.replace(".pdf", "").replace(".", "_").replace(" ", "_")}.mp3'
        tts.save(filename)
        return response.content