function showAgentCreationWizard() {
    const mainContent = document.querySelector('.main-content');
    const wizard = document.getElementById('agentCreationWizard');
    // Clear the main content area
    mainContent.innerHTML = '';

    // Clone the wizard element and set display to block
    const wizardClone = wizard.cloneNode(true);
    wizardClone.style.display = 'block'; // Make it visible
    mainContent.appendChild(wizardClone);
}
// Function to dynamically create the agent list container
function createAgentListContainer() {
    const mainContent = document.querySelector('.main-content');
    let agentListContainer = document.getElementById('agentList');
    // If the container doesn't exist, create it
    if (!agentListContainer) {
        agentListContainer = document.createElement('div');
        agentListContainer.id = 'agentList';
        mainContent.appendChild(agentListContainer);
    }
    return agentListContainer;
}


function loadAndDisplayRootAgents() {
    var savedAgents = JSON.parse(localStorage.getItem('agents')) || [];
    var pipelineContainer = document.getElementById('pipelineContainer');
    pipelineContainer.innerHTML = ''; // Clear previous dropdown if exists

    if (savedAgents.length > 0) {
        const selectDropdown = document.createElement('select');
        selectDropdown.id = 'pipelineAgentSelect';
        savedAgents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.name;
            option.textContent = agent.name;
            selectDropdown.appendChild(option);
        });
        pipelineContainer.appendChild(selectDropdown);
    }
}

function createSaveButton() {
    const pipelineContainer = document.getElementById('pipelineContainer');
    const saveButton = document.createElement('button');
    saveButton.id = 'saveButton';
    saveButton.setAttribute('onclick', 'savePipeline()');
    saveButton.textContent = 'Save Pipeline';
    pipelineContainer.appendChild(saveButton);
}

function createRootNode() {
    const pipelineContainer = document.getElementById('pipelineContainer');
    const rootNode = document.createElement('div');
    rootNode.className = 'node';
    rootNode.id = 'rootNode';
    const rootAgentName = document.createElement('div');
    rootAgentName.id = 'rootAgentName';
    rootAgentName.textContent = 'Select a Root Agent';
    rootNode.appendChild(rootAgentName);
    //const buttonContainer = document.createElement('div');
    //buttonContainer.id = 'buttonContainer';
    //rootNode.appendChild(buttonContainer);
    const addAgentButton = document.createElement('button');
    addAgentButton.id = 'addRootAgentButton';
    addAgentButton.setAttribute('onclick', 'setRootAgent(this)');
    addAgentButton.textContent = 'Set Root Agent';
    rootNode.appendChild(addAgentButton);
    pipelineContainer.appendChild(rootNode);
}


// Function to dynamically create the pipeline container
function createPipelineContainer() {
    const mainContent = document.querySelector('.main-content');
    let pipelineContainer = document.getElementById('pipelineContainer');
    // If the container doesn't exist, create it
    if (!pipelineContainer) {
        pipelineContainer = document.createElement('div');
        pipelineContainer.id = 'pipelineContainer';
        pipelineContainer.style.display = 'block';
        mainContent.appendChild(pipelineContainer);
        // Create the start button
        loadAndDisplayRootAgents();
        createSaveButton();
        createRootNode();
    }
    return pipelineContainer;
}


function createChildrenContainer(parentNode) {
    var container = document.createElement('div');
    container.className = 'children';
    parentNode.appendChild(container);
    return container;
  }

  function updateLines(container) {
    // Adjust the height of the line before the first child to connect it to the parent button
    var children = Array.from(container.children);
    if (children.length > 0) {
      var firstLine = children[0].querySelector('::before');
      if (firstLine) {
        firstLine.style.height = `${container.parentNode.querySelector('button').offsetHeight + 10}px`;
      }
    }
  }  