const canvas = document.getElementById("mapCanvas");
const ctx = canvas.getContext("2d");

// Map data and offsets
let mapData = null;
let offsetX = canvas.width / 2;
let offsetY = canvas.height / 2;

// Replay variables
let isReplaying = false;
let replayIndex = 0;

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
    if (isDragging) {
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

// Button functionality
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

document.getElementById("replay-route").addEventListener("click", () => {
    if (!mapData || !mapData.path.length) return;
    isReplaying = true;
    replayIndex = 0;

    function replayStep() {
        if (!isReplaying || replayIndex >= mapData.path.length) {
            isReplaying = false;
            return;
        }

        const [x, y] = mapData.path[replayIndex];
        offsetX = canvas.width / 2 - x;
        offsetY = canvas.height / 2 - y;
        replayIndex++;
        drawMap();
        requestAnimationFrame(replayStep);
    }

    replayStep();
});