Create a webapp with a textbox that allows a user to input a prompt to send to chatgpt. Allow the user to select between a list of characters such as:

def Actor():
    systemprompt = """You are an Actor in the movie industry so you have experience behind the scenes in the movie industry. You love to talk about your experiences as an actor aswell as a producer."""
    return systemprompt

def King():
    systemprompt = """You are a king, everyone shall respect you and your name. You will not let mere mortals address a king without respect."""
    return systemprompt

def CodingExpert():
    systemprompt = """You are A professional software developer with 50 years of experience. You have continuously kept up with every software programming update, people say you are a genius! You know everything about code like the back of your hand, you snore at any algorithm smaller than a 50 step solution."""
    return systemprompt


class ChatGPTAgent:
    def __init__(self, prompt):
        self.prompt = prompt

    # Initialize a session with OpenAI's chat models
    @staticmethod
    def chat_with_gpt3(prompt, systemprompt):
        messages = [{"role": "user", "content": prompt}]
        if systemprompt:
            messages.insert(0, {"role": "system", "content": systemprompt})
        else:
            messages.insert(0,{"role": "system", "content": "You are a helpful AI assistant"})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.9
        )
        return response['choices'][0]['message']['content']
            # Initialize a session with OpenAI's chat models