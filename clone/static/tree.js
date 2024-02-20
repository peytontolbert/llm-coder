
function findAgentById(agent, id) {
    if (agent.id === id) {
        return agent;
    }
    for (let child of agent.children) {
        let result = findAgentById(child, id);
        if (result) {
            return result;
        }
    }
    return null;
}
function updateTreeVisualization() {
    const treeContainer = document.getElementById('pipelineContainer');
    treeContainer.innerHTML = ''; // Clear the container
    createTree(treeContainer, agentTree); // Recreate the tree with updated data
}
