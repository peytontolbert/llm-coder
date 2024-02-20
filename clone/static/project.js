    // Check local storage for logged in status and name
    function checkLogin() {
        const name = localStorage.getItem('username');

        if (name) {
            // User is logged in, retrieve projects
            getProjects(name);
        } else {
            // Handle the case where the user is not logged in
            console.log('User not logged in.');
            // Redirect to login page or show login form
        }
    }

function loadProject(projectId) {
    console.log('Loading project for editing:', projectId);
    // Fetch the agents for the selected project  
    message = { 'project_id': projectId, 'user': localStorage.getItem('username')}
    fetch('/loadproject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    })
    .then(response => response.json())
    .then(data => {
        localStorage.setItem('currentProject', projectId);
        showAgentCreationWizard();
        if (data.agents && data.agents.length > 0) {
            // Populate main window with agents
            console.log("agents found")
            populateAgents(data.agents);
        } else {
            // Show agent creation wizard if no agents are found
            console.log("no agents found")
            createPipelineContainer();
        }
    })
    .catch((error) => {
        console.error('Error fetching agents:', error);
    });
}

function getProjects(username) {
    fetch('/getprojects', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user: username }),
    })
    .then(response => response.json())
    .then(data => {
        populateProjectList(data.projects);
    })
    .catch((error) => {
        console.error('Error fetching projects:', error);
    });
}

function saveProjectPipeline() {
    const message = {
        username: localStorage.getItem('username'),
        project:  localStorage.getItem('currentProject'),
        pipeline: agentTree
    }
    fetch('/saveproject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    })
}

function populateProjectList(projects) {
    const sidebar = document.getElementById('projectListSidebar');
    projects.forEach(project => {
        const projectItem = document.createElement('div');
        projectItem.className = 'project-item';
        projectItem.innerHTML = `
            <h3 class="project-name" onclick="loadProject('${project.project_id}')">${project.projectname}</h3>
            <button onclick="chatWithWorkflow('${project.project_id}')">Chat with Workflow</button>
        `;
        sidebar.appendChild(projectItem);
    });
}
