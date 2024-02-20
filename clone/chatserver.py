from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS, cross_origin
import json
import threading
import os
import zipfile
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'])
users = {}
projects = {}
agents = {}
unread_chats = []
awaiting_agent_chats = []
agent_response_chats = []
# Function to save messages to a JSON file
def save_messages():
    # Create a lock to synchronize access to the messages list
    with app.app_context():
        data = { 
            'projects': projects,
            'users': users,
            'agents': agents,
            'unread_chats': unread_chats,
            'awaiting_agent_chats': awaiting_agent_chats,
            'agent_response_chats': agent_response_chats 
                }
        # Save the messages list to a JSON file
        with open('messages.json', 'w') as f:
            json.dump(data, f)

    # Schedule the next save in 5 minutes
    threading.Timer(30, save_messages).start()

def load_projects():
    try:
        # Open the JSON file and load projects into the global dictionary
        with open('messages.json', 'r') as f:
            data = json.load(f)
            global projects
            projects = data.get('projects', {})  # Use an empty dictionary if 'projects' is not found
    except FileNotFoundError:
        print("The messages.json file was not found.")
    except json.JSONDecodeError:
        print("There was an error decoding the JSON data from the file.")

# Call this function when your application starts to load existing projects
load_projects()
# Start saving messages in the background
save_messages()

print(projects)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route("/getprojects", methods=["POST"])
def getprojects():
    data = request.get_json()
    user = data.get('user')
    print(user)
    user_projects = []
    for project_id, project_info in projects.items():
        if project_info['user'] == user:
            user_projects.append({"projectname":project_info.get('projectname', 'Unnamed project'), 'project_id':project_id})
    if user_projects:
        return jsonify({'status': 'success', 'projects': user_projects}), 200
    else:
        return jsonify({'status': 'failure', 'error': 'No projects found'}), 400

@app.route("/createproject", methods=["POST"])
def newproject():
    data = request.get_json()
    user = data.get('user')
    projectname = data.get('projectname')
    project_id = str(uuid.uuid4())

    if user not in users:
        users[user] = []

    new_project = {'projectname': projectname, 'project_id': project_id}
    users[user].append(new_project)
    new_project2 = {'projectname': projectname, 'user': user, 'agents': [], 'chats': {}}
    projects[project_id] = new_project2
    return jsonify({'status': 'success', 'project_id': project_id}), 200

@app.route("/loadproject", methods=["POST"])
def loadproject():
    data = request.get_json()
    user = data.get('user')
    projectid = data.get('project_id')

    if projectid not in projects:
        return jsonify({'status': 'failure', 'error': 'Project not found'}), 400
    else:
        return jsonify({'status': 'success', 'project': projects[projectid]}), 200

@app.route("/createagent", methods=["POST"])
def newagent():
    data = request.get_json()
    user = data.get('user')
    agentname = data.get('agentname')
    agent_id = str(uuid.uuid4())
    agents[user].append({'agentname': agentname, 'agent_id': agent_id})
    return jsonify({'status': 'success', 'agent_id': agent_id }), 200

@app.route("/saveproject", methods=["POST"])
def saveproject():
    data = request.get_json()
    print(data)
    project_id = data.get('project')
    user = data.get('username')
    agents = data.get('pipeline')
    if project_id is None:
        return jsonify({'status': 'failure', 'error': 'Project not found'}), 400
    else:
        projects[project_id] = {'user': user, 'pipeline': agents}
        save_messages()
    return jsonify({'status': 'success', 'message': 'Project Saved'}), 200

@app.route("/sendmessage", methods=["POST"])
def sendmessage():
    global projects, unread_chats
    data = request.get_json()
    project_id = data.get('project_id')
    user = data.get('username')
    message = data.get('message')
    if project_id is None:
        return jsonify({'status': 'failure', 'error': 'Project not found'}), 400
    project = projects[project_id]
    if project['user'] != user:
        return jsonify({'status': 'failure', 'error': 'User not authorized'}), 401
    pipeline = project['pipeline']
    chat = {'user': user, 'message': message, 'project_id': project_id, 'pipeline': pipeline}
    unread_chats.append(chat)
    save_messages()
    return jsonify({'status': 'success', 'message': 'Message Saved'}), 200

@app.route("/helpermessages", methods=["GET"])
def helpermessagess():
    global unread_chats
    messages_to_process = []
    # Transfer all unread chats to messages_to_process
    messages_to_process.extend(unread_chats)
    awaiting_agent_chats.extend(messages_to_process)
    unread_chats.clear()  # Clear the global unread_chats list

    if not messages_to_process:
        print('No unread messages')
        return jsonify({'messages': 'No unread messages'}), 404
    

    return jsonify({'messages': messages_to_process}), 200

@app.route("/agentresponse", methods=["POST"])
def agentresponse():
    global awaiting_agent_chats, agent_response_chats
    data = request.get_json()
    project_id = data.get('project_id')
    user = data.get('user')
    response = data.get('response')
    print(f'agent response: {response}')
    # Find and remove the chat from awaiting_agent_chats
    awaiting_agent_chats = [chat for chat in awaiting_agent_chats if not (chat['project_id'] == project_id and chat['user'] == user)]
    
    # clear the chat in awaiting_agent_chats with project_id
    response_chat = {
        'user': user,
        'message': response,
        'project_id': project_id
    }
    agent_response_chats.append(response_chat)
    save_messages()
    return jsonify({'status': 'success', 'message': 'Message Saved'}), 200

@app.route("/checkresponses", methods=["POST"])
def checkresponses():
    global agent_response_chats
    data = request.get_json()
    project_id = data.get('project_id')
    user = data.get('user')
    # Find and remove the chat from awaiting_agent_chats
    response_chat = [chat for chat in agent_response_chats if (chat['project_id'] == project_id and chat['user'] == user)]
    print(response_chat)
    if not response_chat:
        return jsonify({'status': 'failure', 'error': 'No response found'}), 204
    else:
        agent_response_chats = [chat for chat in agent_response_chats if not (chat['project_id'] == project_id and chat['user'] == user)]
        return jsonify({'status': 'success', 'message': response_chat}), 200


def unzip_and_save(zip_file_path, destination_folder):
    """
    Unzips a .zip file and saves its contents to a specified destination folder.

    :param zip_file_path: The path to the .zip file.
    :param destination_folder: The folder where the contents of the .zip file will be saved.
    """
    # Check if the zip file exists
    if not os.path.exists(zip_file_path):
        return "Zip file does not exist."

    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Unzip the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    return f"Contents extracted to {destination_folder}"

def run_server():
    app.run(port=5000)  # Run the Flask app on port 5000

    
if __name__ == "__main__":
    run_server()