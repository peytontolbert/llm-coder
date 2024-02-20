const agents = []; // Array of AgentNode objects
let agentTree = {
    id: "root",
    name: "Start Agent",
    children: []
};
// Simplified example of a node
class AgentNode {
    constructor(id, name, description, prompt, functions, instanceId, children = [], startAgent = false) {
        this.id = id;
        this.instanceId = instanceId || Date.now();
        this.name = name;
        this.description = description;
        this.prompt = prompt;
        this.functions = functions;
        this.children = children; // Array of AgentNode references
        this.element = null; // DOM element for the agent
        this.connectionElements = []; // DOM elements for the connections
        this.startAgent = startAgent;
    }

    // Creates the DOM element for the agent
    createElement() {
        if(this.element === null) {
            this.element = document.createElement('div');
            this.element.className = 'agent';
            this.element.textContent = `${this.name} - ${this.description}`; // Or whatever you want to display
            this.element.id = this.instanceId;
        }
        
        return this.element;
    }

    // Adds a child node and creates a connection
    addChild(childNode) {
        // Create a connection line between this node and the child
        positionChildrenNode(childNode, this);
        drawConnection(this.element, childNode.element);
        this.children.push(childNode);
    }
}

function createAgent() {
    const agentName = document.getElementById('agent-name').value;
    const agentPrompt = document.getElementById('agent-prompt').value;
    const agentFunctions = document.getElementById('agent-functions').value; // This assumes a comma-separated list of functions
    const agentDescription = document.getElementById('agent-description').value;
    
    // Create an agent object
    const agent = {
        id: Date.now(), // A simple way to generate a unique ID for each agent
        name: agentName,
        description: agentDescription,
        prompt: agentPrompt,
        functions: agentFunctions
    };

    // Retrieve existing agents from local storage or initialize an empty array if none
    const localagents = JSON.parse(localStorage.getItem('agents')) || [];

    // Add the new agent to the array and save it back to local storage
    localagents.push(agent);
    localStorage.setItem('agents', JSON.stringify(localagents));

    // Clear input fields after creation
    document.getElementById('agent-name').value = '';
    document.getElementById('agent-prompt').value = '';
    document.getElementById('agent-functions').value = '';

}
function LoadAgentList() {
    const agentListContainer = createAgentListContainer();
    agentListContainer.innerHTML = ''; // Clear existing content
    const agents = JSON.parse(localStorage.getItem('agents')) || [];
    if (agents) {
        console.log("loading agent list")
        agents.forEach(agent => {
            const agentDiv = document.createElement('div');
            agentDiv.className = 'agent';
            agentDiv.innerHTML = `<h3>${agent.name}</h3><p>Description: ${agent.description}</p>`;
            agentListContainer.appendChild(agentDiv);
        });
    } else {
        console.error('Agents found in storage');
    }
}
function appendChildren(parentInstance, children, agents, startDiv) {
    children.forEach(childId => {
        // Find the child agent from the list of all agents using the childId
        const childAgent = agents.find(a => a.id === childId);
        if (childAgent) {
            localSavedAgent = localStorage.getItem('agents').find(agents => agents.id === childAgent.id)
            const agentInstance = new AgentNode(localSavedAgent.id, localSavedAgent.name, localSavedAgent.description, localSavedAgent.prompt, localSavedAgent.functions );
            agentInstance.createElement();
            parentInstance.addChild(childDiv);
            childDiv = startDiv.appendChild(agentInstance.element)
            // If this child agent has its own children, recurse
            if (childAgent.children && childAgent.children.length > 0) {
                // Create a container for the children to keep the hierarchy visual  
                const childInstance = new AgentNode(localSavedAgent.id, localSavedAgent.name, localSavedAgent.description, localSavedAgent.prompt, localSavedAgent.functions );
                childInstance.createElement(); 
                addAgentToTree(parentInstance.id, childInstance)
                // Recursively append the children of the current child agent
                appendChildren(childInstance, childAgent.children, agents, childDiv);             
            }
        }
    });
}
function createAgentTree(agentData) {
    let parentElement = document.getElementById('pipelineContainer');
    const agentDiv = document.createElement('div');
    agentDiv.className = 'agent';
    agentDiv.textContent = agentData.name;
    agentDiv.id = agentData.id;
    parentElement.appendChild(agentDiv);
  
    if (agentData.children && agentData.children.length > 0) {
      const childrenContainer = document.createElement('div');
      childrenContainer.className = 'children-container';
      agentDiv.appendChild(childrenContainer);
  
      agentData.children.forEach(childAgentData => {
        const siblingContainer = document.createElement('div');
        siblingContainer.className = 'siblings-container';
        childrenContainer.appendChild(siblingContainer);
  
        createAgentTree(siblingContainer, childAgentData);
      });
    }
  }
function addAgentToTree(parentId, agentInstance) {
      let parentAgent = findAgentById(agentTree, parentId);
      console.log('parentId', parentId)
      console.log('agentInstance', agentInstance)
      if (parentAgent) {
          const newAgent = {
              id: agentInstance.instanceId, // You need to define this function
              name: agentInstance.name,
              children: []
          };
          parentAgent.children.push(newAgent);
          updateTreeVisualization();
      } else {
          console.error('Parent agent not found');
      }
  }
  
  
function showAgentDropdown(buttonid, parentInstanceId) {
    console.log('showAgentSelection called'); // Debugging line
    // Retrieve saved agents from local storage
    const savedAgents = JSON.parse(localStorage.getItem('agents')) || [];
    const button = document.getElementById('button-'+buttonid);
    console.log('Saved agents:', savedAgents); // Debugging line
    console.log('button', buttonid); // Debugging line
    if(button==="button-pipelineContainer") {
        parent = createPipelineContainer()
    }
    else {
        parent = button.parentNode; // Get the parent element of the button
    }
    // Check if there are any saved agents
    if (savedAgents.length === 0) {
        console.log('No saved agents found.'); // Debugging line
        // If no saved agents, maybe show a message or create an agent
        // For example:
        const noAgentsMsg = document.createElement('p');
        noAgentsMsg.textContent = 'No saved agents found. Please create one.';
        const pipelineContainer = createPipelineContainer();
        pipelineContainer.appendChild(noAgentsMsg);
        return; // Exit the function
    }
    // If there are saved agents, proceed to create the dropdown
    const selectDropdown = document.createElement('select');
    selectDropdown.id = 'agentSelect';
    savedAgents.forEach(agent => {
        const option = document.createElement('option');
        option.value = agent.id;
        option.textContent = agent.name;
        selectDropdown.appendChild(option);
    });
    // Add a button for confirming the agent selection
    const container = document.createElement('div');
    container.id = 'container-'+parentInstanceId;
    const addButton = newAddAgentButton(container, parentInstanceId, selectDropdown);
    container.appendChild(selectDropdown);
    container.appendChild(addButton);
    parent.replaceChild(container, button);
}
function addAgentToPipeline(container, agentId, parentId ) {
    // Get the selected agent ID from the dropdown
    const savedAgents = JSON.parse(getSavedAgents()); // Retrieve the agents array from local storage or backend
    console.log(savedAgents)
    console.log(typeof savedAgents); // Should be 'object' since arrays are objects in JavaScript
    console.log(Array.isArray(savedAgents)); // Should be true if it's an array
    console.log("container", container)
    console.log("parentId", parentId)
    console.log("agentId", agentId)
    const selectedAgent = savedAgents.find(agent => {
        console.log('Comparing:', agent.id, agentId, String(agent.id) === String(agentId))
        return String(agent.id) === String(agentId);
    });
    console.log(selectedAgent)
    if (selectedAgent) {
        // Clear the existing container contents
        const agentInstance = new AgentNode(selectedAgent.id, selectedAgent.name, selectedAgent.description, selectedAgent.prompt, selectedAgent.functions);
        instancediv = agentInstance.createElement();
        console.log('agentInstance', agentInstance);
        if(parentId) {
            let parent = container.parentNode; // Get the parent element of the button
            container.innerHTML = '';
            const parentAgentNode = agents.find(agent => String(agent.id) === String(parentId));
            if (parentAgentNode) {
                parentAgentNode.addChild(agentInstance);
                // Add a button to this agent's div to allow adding new connections from this agent
                addAgentToTree(parentAgentNode.instanceId, agentInstance.instanceId)
                container.appendChild(agentInstance);
                agents.push(agentInstance);
                const container = document.createElement('div');
                container.id = 'container-'+parentId;
                const newConnectionButton = createNewConnectionButton(parent.id);
                parent.appendChild(newConnectionButton);
                positionChildrenNode(newConnectionButton, parent)
                // container.appendChild(instancediv);
            }
        } else {            
            console.log('container', container);
            agentInstance.startAgent = true;
            createAgentTree(agentInstance)
            // container.appendChild(instancediv);
            console.log('agents', agents)
            agentInstance.element = positionNode(agentInstance);
            agents.push(agentInstance);
            //positionChildrenNode(newConnectionButton, agentInstance)
            container.appendChild(agentInstance);
        }
        const newConnectionButton = createNewConnectionButton(agentInstance.instanceId);
        positionChildrenNode(newConnectionButton, agentInstance)
        agentInstance.appendChild(newConnectionButton);

    } else {
        console.error('Selected agent not found');
    }
}
function populatePipeline(agents) {
    // Assuming you have an element with id 'pipeline' to append agents to
    const pipelineContainer = createPipelineContainer();
    pipelineContainer.innerHTML = ''; // Clear existing agents
    const startAgent = agents.find(agent => agent.startAgent === true);

    localSavedAgents = localStorage.getItem('agents') || [];
    localSavedStartAgent = localSavedAgents.find(agents => agents.id === startAgent.id)
    if(localSavedStartAgent) {
        const agentInstance = new AgentNode(localSavedStartAgent.id, localSavedStartAgent.name, localSavedStartAgent.description, localSavedStartAgent.prompt, localSavedStartAgent.functions, startAgent = true);
        agentInstance.createElement();
        agentInstance.positionNode(agentInstance);
        createTree(pipelineContainer, agentInstance)
        agents.push(agentInstance);
        // recursively append children if the start agent has any
        if (startAgent.children && startAgent.children.length > 0) {
            appendChildren(agentInstance, startAgent.children, agents, startDiv);
        }
    }
  }
  
  
// Function to draw the connections based on the positions
function drawConnection( agentDiv, parentAgentDiv ) {
    // Create a new div element for the line
    const line = document.createElement('div');
    line.className = 'connection-line';
    
    // Get the position of the parent and agent divs
    const parentRect = parentAgentDiv.getBoundingClientRect();
    const agentRect = agentDiv.getBoundingClientRect();
    
    // Calculate the center position of the parent and agent divs
    const startX = parentRect.left + parentRect.width / 2 + window.scrollX;
    const startY = parentRect.top + parentRect.height / 2 + window.scrollY;
    const endX = agentRect.left + agentRect.width / 2 + window.scrollX;
    const endY = agentRect.top + agentRect.height / 2 + window.scrollY;
    
    // Calculate the distance between the two points
    const length = Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2);
    
    // Calculate the angle between the two points
    const angle = Math.atan2(endY - startY, endX - startX) * (180 / Math.PI);
    
    // Set the position, width, and rotation of the line
    line.style.position = 'absolute';
    line.style.top = `${startY}px`;
    line.style.left = `${startX}px`;
    line.style.width = `${length}px`;
    line.style.transform = `rotate(${angle}deg)`;
    line.style.transformOrigin = '0 0';
    
    // Additional styling for the line
    line.style.height = '2px'; // Thickness of the line
    line.style.backgroundColor = '#000'; // Color of the line
    
    // Append the line to the body or another container
    document.body.appendChild(line);
}

function positionChildrenNode(childNode, parentNode) {
    const horizontalSpacing = 100; // Horizontal space between sibling nodes
    const verticalSpacing = 100; // Vertical space between parent and child nodes

    // Calculate the number of existing children including the new child
    const numberOfChildren = parentNode.children.length + 1;

    console.log('childNode', childNode)
    console.log('parentNode', parentNode)
    // Calculate the starting X position for the first child
    const startX = parentNode.position.x - horizontalSpacing * (numberOfChildren - 1) / 2;

    // Calculate the position for the new child node
    childNode.position = {
        x: startX + (numberOfChildren - 1) * horizontalSpacing,
        y: parentNode.position.y + verticalSpacing
    };
    console.log('childNode.position', childNode.position)
    // Update the child node's DOM element position
    if(childNode.element) { 
        childNode.element.className = 'agent';
        childNode.element.style.left = `${childNode.position.x}px`;
        childNode.element.style.top = `${childNode.position.y}px`;
    } else {
        childNode.className = 'agent';
        childNode.style.left = `${childNode.position.x}px`;
        childNode.style.top = `${childNode.position.y}px`;
    }
}

// Function to position agents in a tree-like structure
function positionNode(agentNode, parentAgentDiv = null) {
    if(!parentAgentDiv) {
        agentNode.position = { x: 50, y: 50 };
    } else {
        positionChildrenNode(agentNode, parentAgentDiv);
    }
    // Update the DOM element's position based on agentNode.position
    agentNode.element.style.left = `${agentNode.position.x}px`;
    agentNode.element.style.top = `${agentNode.position.y}px`;
    return agentNode.element;
}

// Utility function to get saved agents
function getSavedAgents() {
    localagents = localStorage.getItem('agents') || [];
    return localagents;
}
