// Event listener for creating a new project
document.getElementById('createproject').addEventListener('click', function() {
    const projectName = document.getElementById('project-name').value;
    const startAgent = document.getElementById('start-agent').value;
    const name = localStorage.getItem('username');
    if (startAgent){
        message = { 'user': name, 'projectname': projectName, 'startagent': startAgent}
    } else {
        message = { 'user': name, 'projectname': projectName }
    }
    console.log(projectName)
    fetch('/createproject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    })
    .then(response => response.json())
    .then(data => {
        // Handle response
        console.log(data);
        // You can now add the new project to the sidebar
    })
    .catch((error) => {
        console.error('Error creating project:', error);
    });
});

// Event listener for creating a new agent
document.getElementById('createagent').addEventListener('click', function() {
    const agentName = document.getElementById('agent-name').value;
    const agentPrompt = document.getElementById('agent-prompt').value;
    const agentFunctions = document.getElementById('agent-functions').value; // This assumes a comma-separated list of functions
    message = { name: agentName, prompt: agentPrompt, functions: agentFunctions.split(',') }
    fetch('/createagent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    })
    .then(response => response.json())
    .then(data => {
        // Handle response
        console.log(data);
        // You can now add the new agent to the project
    })
    .catch((error) => {
        console.error('Error creating agent:', error);
    });
});


function chatWithWorkflow(projectId) {
console.log('Starting chat with project workflow:', projectId);
// You would add logic here to start the chat with the project's workflow
}

function saveProject() {
    // Logic to save the current state of the project with the project id, user, and active agents
    // This will likely involve iterating over DOM elements to gather agent data
    // and sending a POST request to your '/saveproject' endpoint
}
 

// Add JavaScript to handle sidebar toggling
function toggleSidebar() {
    var sidebar = document.getElementById('projectListSidebar');
    sidebar.style.display = sidebar.style.display === 'block' ? 'none' : 'block';
}
// Run checkLogin on page load
document.addEventListener('DOMContentLoaded', checkLogin);