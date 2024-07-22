import re

from google._upb._message import RepeatedCompositeContainer
from google.generativeai import GenerativeModel, configure

from app.core.config import config
from app.google_api_ai.client import Client


class Controller:
    def __init__(self, model: GenerativeModel | None = None):
        self.model = model
        if not self.model:
            self.update_model()

    def update_model(self) -> None:
        configure(api_key=config.API_KEY)
        client = Client(model_name=config.GENERATIVE_MODEL_NAME, api_key=config.API_KEY)
        self.model = client.model

    async def check_for_inappropriate_content(self, content: str) -> bool:
        response = await self.model.generate_content_async(
            f"Please check following content for the presence of obscene language, insults, hate speech, etc.: "
            f"{content}."
        )
        response_pb = response.candidates
        safety_ratings_text = re.findall(r'safety_ratings {.*?probability: .*?\n}', str(response_pb), re.DOTALL)
        safety_ratings_dict = {}
        for rating in safety_ratings_text:
            category = re.search(r'category: (HARM_CATEGORY_[A-Z_]+)', rating).group(1)
            probability = re.search(r'probability: ([A-Z]+)', rating).group(1)
            safety_ratings_dict[category] = probability
        print(safety_ratings_dict)
        if all(value_ == "NEGLIGIBLE" for value_ in safety_ratings_dict.values()):
            print(True)
            return True
        else:
            print(False)
            return False

    async def generate_auto_reply(self, comment: str) -> str | None:
        response = await self.model.generate_content_async(
            f"Please, generate auto-reply on this comment: {comment}. Print auto-reply in ***your reply***. "
            f"Max length 200 characters Thanks"
        )
        response_txt = response.text
        print(response_txt)
        pattern = re.compile(r'\*\*\*(.*?)\*\*\*')
        auto_replies = pattern.findall(response_txt)
        if not auto_replies:
            return
        else:
            print(auto_replies[0])
            return auto_replies[0]


