var agentTree = {
    rootNode: null,
    agents: {}
};
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
function setRootAgent(button) {
    var selectDropdown = document.getElementById('pipelineAgentSelect');
    var selectedAgentId = selectDropdown.value;
    console.log(selectedAgentId)
    var savedAgents = JSON.parse(localStorage.getItem('agents')) || [];
    var selectedAgent = savedAgents.find(agent => agent.name === selectedAgentId);
    if (selectedAgent) {
        document.getElementById('rootAgentName').textContent = selectedAgent.name;
        instance_id = Date.now();
        agentTree.agents[instance_id] = 
        { 
            instance_id: instance_id, 
            id: selectedAgent.id, 
            name: selectedAgent.name, 
            children: [], 
            functions: selectedAgent.functions, 
            prompt: selectedAgent.prompt 
        };
        agentTree.rootNode = instance_id;
        //document.getElementById('rootNode').querySelector('.children').innerHTML = '';
        // Replace the button
         var rootNode = document.getElementById('rootNode');
         rootNode.dataset.agentId = selectedAgent.id; // Set the data-agent-id attribute
         rootNode.dataset.instanceId = instance_id; // Set the data-agent-id attribute
        const oldButton = document.getElementById('addRootAgentButton');
        console.log(oldButton)
        const addAgentButton = document.createElement('button');
        addAgentButton.id = 'addAgentButton';
        addAgentButton.textContent = 'Set Agent';
        addAgentButton.setAttribute('onclick', 'addAgent(this)'); // Remove the onclick handler
        console.log(addAgentButton)
        rootNode.replaceChild(addAgentButton, oldButton);
        // Optionally clear existing children if you want to reset the tree
    }
}

function addAgent(button) {
  var parentNode = button.parentNode;
  var parentInstanceId = parentNode.dataset.instanceId; // Assuming you set data-agent-id on each node
  var childrenContainer = parentNode.querySelector('.children') || createChildrenContainer(parentNode);
    // Retrieve the selected agent from the dropdown
    var selectDropdown = document.getElementById('pipelineAgentSelect');
    var selectedAgentId = selectDropdown.value;
    var savedAgents = JSON.parse(localStorage.getItem('agents')) || [];
    var selectedAgent = savedAgents.find(agent => agent.name === selectedAgentId);
    if (selectedAgent) {
        instance_id = Date.now();
        // Create a new child node in the agent tree
        var childAgent = {
            instance_id: instance_id,
            id: selectedAgent.id,
            name: selectedAgent.name,
            children: [], 
            functions: selectedAgent.functions, 
            prompt: selectedAgent.prompt
        };
        // Append the child agent to the parent in the agent tree
        if (agentTree.agents[parentInstanceId]) {
            agentTree.agents[parentInstanceId].children.push(childAgent);
        }
        agentTree.agents[instance_id] = childAgent;
        // Create a new div element for the agent node
        var node = document.createElement('div');
        node.className = 'node';
        node.dataset.agentId = selectedAgent.id; // Set the data-agent-id attribute
        node.dataset.instanceId = instance_id; // Set the data-agent-id attribute
        node.innerHTML = '<div>' + selectedAgent.name + '</div><button onclick="addAgent(this)">Add Agent</button>'; // Use the selected agent's name

        // Create a container for the child
        var child = document.createElement('div');
        child.className = 'child';
        child.appendChild(node);
        
        // Append the child container to the children container
        childrenContainer.appendChild(child);

        // Update lines connecting nodes
        updateLines(childrenContainer);
    }
}

function savePipeline() {
    var pipeline = {
        rootAgent: agentTree.rootNode,
        agents: agentTree.agents
    };
    let storagePipeline = localStorage.getItem('pipeline');
    const currentProject = localStorage.getItem('currentProject');
    if (storagePipeline === null) {
        storagePipeline = {};
    } else {
        // Parse storagePipeline if it's a valid JSON string
        storagePipeline = JSON.parse(storagePipeline);
    }
    storagePipeline[currentProject] = pipeline;
    localStorage.setItem('pipeline', JSON.stringify(pipeline));
    saveProjectPipeline();

}

function loadAndDisplayAgents() {
    var savedAgents = JSON.parse(localStorage.getItem('agents')) || [];
    var dropdownContainer = document.getElementById('agentDropdownContainer');
    dropdownContainer.innerHTML = ''; // Clear previous dropdown if exists

    if (savedAgents.length > 0) {
        const selectDropdown = document.createElement('select');
        selectDropdown.id = 'agentSelect';
        savedAgents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.name;
            option.textContent = agent.name;
            selectDropdown.appendChild(option);
        });
        
        dropdownContainer.appendChild(selectDropdown);
    }
}