# webapp.py
from flask import Flask, request, jsonify
from chatgpt import ChatGPTAgent, Actor, King, CodingExpert

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return '<h1>Welcome to the ChatGPT WebApp!</h1><p>To access the chat interface, go to /chat</p>'

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        prompt = request.form['input-prompt']
        character = request.form['select-character']
        if character == 'Actor':
            systemprompt = Actor()
        elif character == 'King':
            systemprompt = King()
        elif character == 'CodingExpert':
            systemprompt = CodingExpert()
        else:
            systemprompt = None
        response = ChatGPTAgent.chat_with_gpt3(prompt, systemprompt)
        return jsonify({'chat_message': response})
    else:
        return '''
            <h1>Chat with ChatGPT</h1>
            <form method="post">
                <label for="input-prompt">Your message:</label><br>
                <input type="text" id="input-prompt" name="input-prompt"><br>
                <label for="select-character">Select a chat partner:</label>
                <select id="select-character" name="select-character">
                    <option value="Actor">Actor</option>
                    <option value="King">King</option>
                    <option value="CodingExpert">Coding Expert</option>
                </select><br><br>
                <input type="submit" id="submit-button" value="Submit">
            </form>
        '''

class WebApp:
    def __init__(self, prompt):
        self.prompt = prompt

    def start(self):
        app.run(debug=False)