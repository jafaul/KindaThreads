import google.generativeai as genai


class Client:
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.api_key = api_key
        self.model = None
        if self.model is None:
            self.model = self.__get_model()

    def __get_model(self):
        model = genai.GenerativeModel(self.model_name)
        return model
