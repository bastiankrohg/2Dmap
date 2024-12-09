const canvas = document.getElementById("mapCanvas");
const ctx = canvas.getContext("2d");

// Map data and offsets
let mapData = null;
let offsetX = canvas.width / 2;
let offsetY = canvas.height / 2;

// Replay variables
let isReplaying = false;

// Mouse drag and hover functionality
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;
let hoveredObject = null;

// Fetch map data
fetch('/maps/latest.json')
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        mapData = data;

        // Set initial position to the end of the path
        if (mapData.path && mapData.path.length) {
            const end = mapData.path[mapData.path.length - 1];
            offsetX = canvas.width / 2 - end[0];
            offsetY = canvas.height / 2 - end[1];
        }

        populateLists();
        drawMap();
    })
    .catch(error => console.error("Error loading map data:", error));

// Update HUD
function updateHUD() {
    const hud = document.getElementById("hud");
    if (!mapData) {
        hud.textContent = "Loading map data...";
        return;
    }
    const roverPos = mapData.rover_pos;
    const roverAngle = mapData.rover_angle;
    const mastAngle = mapData.mast_angle;

    hud.textContent = `Rover Position: (${roverPos[0].toFixed(2)}, ${roverPos[1].toFixed(2)}) | Heading: ${roverAngle.toFixed(2)}° | Mast: ${mastAngle.toFixed(2)}°`;
}

function populateList(type) {
    const listElement = document.getElementById(`${type}-list`);
    listElement.innerHTML = ""; // Clear existing items

    const items = mapData[type]; // 'resources' or 'obstacles'
    if (!items || items.length === 0) {
        listElement.innerHTML = `<li>No ${type} detected.</li>`;
        return;
    }

    items.forEach((item, index) => {
        const li = document.createElement("li");
        const label = item.object || "Unknown";
        const position = item.position ? `(${item.position[0].toFixed(2)}, ${item.position[1].toFixed(2)})` : "(N/A)";
        li.textContent = `${index + 1}. ${label} at ${position}`;
        li.addEventListener("click", () => highlightItem(item.position));
        listElement.appendChild(li);
    });
}

function highlightItem(position) {
    offsetX = canvas.width / 2 - position[0];
    offsetY = canvas.height / 2 - position[1];
    drawMap();
    ctx.strokeStyle = "yellow";
    ctx.lineWidth = 2;
    ctx.strokeRect(position[0] + offsetX - 10, position[1] + offsetY - 10, 20, 20);
}

// Replay route function
function replayRoute() {
    if (!mapData || !mapData.path || mapData.path.length === 0) return;

    let i = 0;
    let progress = 0; // Progress between points (0 to 1)

    function animate() {
        if (i >= mapData.path.length - 1) return;

        const [startX, startY] = mapData.path[i];
        const [endX, endY] = mapData.path[i + 1];

        // Interpolate positions
        const currentX = startX + (endX - startX) * progress;
        const currentY = startY + (endY - startY) * progress;

        offsetX = canvas.width / 2 - currentX;
        offsetY = canvas.height / 2 - currentY;

        drawMap();

        // Increment progress
        progress += 0.4; // Adjust speed here
        if (progress >= 1) {
            progress = 0;
            i++; // Move to the next segment
        }

        // Continue animation
        requestAnimationFrame(animate);
    }

    animate();
}

// Check if the mouse is over a resource or obstacle
function checkHover(x, y) {
    hoveredObject = null;

    const mouseX = x - offsetX;
    const mouseY = y - offsetY;

    // Check resources
    mapData.resources.forEach(resource => {
        const resX = resource.position[0];
        const resY = resource.position[1];
        const distance = Math.sqrt((mouseX - resX) ** 2 + (mouseY - resY) ** 2);
        if (distance <= resource.size) {
            hoveredObject = { x: resX + offsetX, y: resY + offsetY, size: resource.size, type: 'resource', data: resource };
        }
    });

    // Check obstacles
    mapData.obstacles.forEach(obstacle => {
        const obsX = obstacle.position[0];
        const obsY = obstacle.position[1];
        const distance = Math.sqrt((mouseX - obsX) ** 2 + (mouseY - obsY) ** 2);
        if (distance <= obstacle.size) {
            hoveredObject = { x: obsX + offsetX, y: obsY + offsetY, size: obstacle.size, type: 'obstacle', data: obstacle };
        }
    });
}

// Display data of clicked object
function handleClick() {
    if (hoveredObject) {
        alert(`Type: ${hoveredObject.type}\nPosition: (${hoveredObject.data.position[0].toFixed(2)}, ${hoveredObject.data.position[1].toFixed(2)})\nSize: ${hoveredObject.data.size}\nObject: ${hoveredObject.data.object}`);
    }
}

// Draw the map
function drawMap() {
    if (!mapData) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update HUD
    updateHUD();

    // Draw path
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 2;
    ctx.beginPath();
    mapData.path.forEach(([x, y], i) => {
        const canvasX = x + offsetX;
        const canvasY = y + offsetY;
        if (i === 0) ctx.moveTo(canvasX, canvasY);
        else ctx.lineTo(canvasX, canvasY);
    });
    ctx.stroke();

    // Draw resources
    mapData.resources.forEach(resource => {
        const resX = resource.position[0] + offsetX;
        const resY = resource.position[1] + offsetY;
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(resX, resY, resource.size, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Draw obstacles
    mapData.obstacles.forEach(obstacle => {
        const obsX = obstacle.position[0] + offsetX;
        const obsY = obstacle.position[1] + offsetY;
        ctx.fillStyle = 'brown';
        ctx.beginPath();
        ctx.arc(obsX, obsY, obstacle.size, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Highlight hovered object
    if (hoveredObject) {
        const { x, y, size, type } = hoveredObject;
        ctx.strokeStyle = type === 'resource' ? 'yellow' : 'orange';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(x, y, size + 5, 0, 2 * Math.PI);
        ctx.stroke();
    }

    // Draw rover
    const roverX = mapData.rover_pos[0] + offsetX;
    const roverY = mapData.rover_pos[1] + offsetY;
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(roverX, roverY, 10, 0, 2 * Math.PI);
    ctx.fill();

    // Draw rover heading
    const roverHeadingX = roverX + Math.cos((mapData.rover_angle * Math.PI) / 180) * 30;
    const roverHeadingY = roverY - Math.sin((mapData.rover_angle * Math.PI) / 180) * 30;
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(roverX, roverY);
    ctx.lineTo(roverHeadingX, roverHeadingY);
    ctx.stroke();

    // Draw mast direction
    const mastHeadingX = roverX + Math.cos((mapData.mast_angle * Math.PI) / 180) * 30;
    const mastHeadingY = roverY - Math.sin((mapData.mast_angle * Math.PI) / 180) * 30;
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(roverX, roverY);
    ctx.lineTo(mastHeadingX, mastHeadingY);
    ctx.stroke();
}

// Handle mouse drag
canvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
});

canvas.addEventListener("mousemove", (e) => {
    if (!isDragging) {
        checkHover(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
        drawMap();
    } else {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        offsetX += dx;
        offsetY += dy;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        drawMap();
    }
});

canvas.addEventListener("mouseup", () => {
    isDragging = false;
});

canvas.addEventListener("mouseleave", () => {
    isDragging = false;
});

canvas.addEventListener("click", handleClick);

// Resources and Obstacles buttons
document.getElementById("resources-toggle").addEventListener("click", () => {
    const list = document.getElementById("resources-list");
    list.style.display = list.style.display === "none" ? "block" : "none";
    populateList("resources");
});

document.getElementById("obstacles-toggle").addEventListener("click", () => {
    const list = document.getElementById("obstacles-list");
    list.style.display = list.style.display === "none" ? "block" : "none";
    populateList("obstacles");
});

// Show Start and Show End buttons
document.getElementById("show-start").addEventListener("click", () => {
    if (!mapData || !mapData.path.length) return;
    const start = mapData.path[0];
    offsetX = canvas.width / 2 - start[0];
    offsetY = canvas.height / 2 - start[1];
    drawMap();
});

document.getElementById("show-end").addEventListener("click", () => {
    if (!mapData || !mapData.path.length) return;
    const end = mapData.path[mapData.path.length - 1];
    offsetX = canvas.width / 2 - end[0];
    offsetY = canvas.height / 2 - end[1];
    drawMap();
});

document.getElementById("replay-route").addEventListener("click", replayRoute);