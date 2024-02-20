import time
import requests
from dotenv import load_dotenv
import openai
import os
load_dotenv()

class ChatGPT:
    def __init__(self):
        pass
    @staticmethod
    def chat_with_gpt3(messages, retries=5, delay=5):
        for i in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.9
                )
                return response['choices'][0]['message']['content']
            except openai.error.ServiceUnavailableError:
                if i < retries - 1:  # i is zero indexed
                    time.sleep(delay)  # wait before trying again
                else:
                    raise  # re-raise the last exception if all retries fail


class AgentServer:
    def __init__(self):
        self.messages = []

    def run(self):
        self.checkmessages()
        print(self.messages)
        while self.messages:
            message = self.messages.pop(0)  # Remove and return the first message
            self.handle_new_message(message)
        time.sleep(10)

    def checkmessages(self):
        try:
            response = requests.get("http://localhost:5000/helpermessages")
            if response.status_code == 200:
                messages_data = response.json()
                self.messages.extend(messages_data['messages'])
            else:
                print("No new messages")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    def handle_new_message(self, message):
        # Assuming the message is a dictionary with necessary fields
        pipeline = message['pipeline']
        user_message = message['message']
        project_id = message['project_id']
        user = message['user']
        agent_responses = []
        print(pipeline)
        current_agent_id = str(pipeline['rootNode'])
        context = f"user:{user_message}"
        while current_agent_id is not None:
            current_agent = pipeline['agents'][current_agent_id]
            agent_name = current_agent['name']
            response = self.process_message_with_agent(context, current_agent)
            context += "\n" + current_agent['name'] + ":" + response
            # Save the agent's response in the list
            agent_responses.append(f'{agent_name}: {response}')

            # Decide the next agent
            children = current_agent['children']
            if children:
                if len(children) == 1:
                    next_agent = children[0]
                else:
                    decision, next_agent = self.decide_next_agent(context, children)
                    if next_agent is None:
                        print("error finding agent, trying decision helper")
                        next_agent = self.decision_helper(decision, children)
                print(f"Next agent: {next_agent}")
                current_agent_id = str(next_agent['instance_id'])
                print(f'current agent id: {current_agent_id}')
            else:
                current_agent_id = None  # No more agents to process
                print("No more agents to process")

        # Send the final response back to the Flask server
        self.send_response_to_server(project_id, agent_responses, user)



        # Send the processed response back to the Flask server
        try:
            response_data = {
                'project_id': project_id,
                'response': response
            }
            response_to_server = requests.post("http://localhost:5000/agentresponse", json=response_data)
            if response_to_server.status_code != 200:
                print("Error sending response back to server")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending response: {e}")




    def process_message_with_agent(self, message, agent):
        agent_prompt = agent['prompt']
        gpt_message = [{"role": "system", "content": agent_prompt}, {"role": "user", "content": message}]
        response = ChatGPT.chat_with_gpt3(gpt_message)
        print(response)
        return response    
    def decision_helper(self, decision, children):
        children_list = []
        for child in children:
            children_list.append(child['name'])
        prompt = """Pick the correct name from the list, that best fits the message:
        [LIST]
        {children_list}"""
        systemprompt = prompt.format(children_list=children_list)
        message = [{"role": "system", "content": systemprompt}, {"role": "user", "content": decision}]
        result = ChatGPT.chat_with_gpt3(message)
        print(result)
        for childname in children_list:
            if childname in result:
                return child
        return None

            

    def decide_next_agent(self, message, children):
        children_choices = [f"{child['name']}: {child['prompt']}" for child in children]
        decider_prompt = """You are an autonomous selection tool. You will decide which agent will most appropriately handle the next task.
        
        [CHOICES]
        {children_choices}
        
        MESSAGE TO HANDLE:"""
        decider_prompt = decider_prompt.format(children_choices="\n".join(children_choices), user_message=message)
        decider_message = [{"role": "system", "content": decider_prompt}, {"role": "user", "content": message}]
        decision = ChatGPT.chat_with_gpt3(decider_message)
        print(f'decision: {decision}')
        # Assume the decision includes the name of the agent
        for child in children:
            if child['name'] in decision:
                return decision, child  # Return the decision text and the next agent's ID

        return decision, None  # If no match, return None for the next agent

    def send_response_to_server(self, project_id, response, user):
        try:    
            print(f'response to server:  {response}')
            response_data = {'project_id': project_id, 'response': response, 'user': user}
            response_to_server = requests.post("http://localhost:5000/agentresponse", json=response_data)
            if response_to_server.status_code != 200:
                print("Error sending response back to server")
            else:
                print("Response sent to server")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending response: {e}")
        


def main():
    agent_server = AgentServer()
    try:
        while True:
            agent_server.run()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        print("performing cleanup")

    print("application exited.")

# Run the AgentServer
if __name__ == "__main__":
    main()