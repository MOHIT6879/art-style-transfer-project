const canvas = document.getElementById('scratchPad');
const ctx = canvas.getContext('2d');
let drawing = false;

// Start Drawing
canvas.addEventListener('mousedown', () => {
    drawing = true;
    ctx.beginPath();
});

// Draw
canvas.addEventListener('mousemove', (event) => {
    if (!drawing) return;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'black';
    ctx.lineTo(event.offsetX, event.offsetY);
    ctx.stroke();
});

// Stop Drawing
canvas.addEventListener('mouseup', () => {
    drawing = false;
    ctx.closePath();
});

// Clear Canvas
document.getElementById('clearCanvas').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

// Submit Canvas
document.getElementById('submitCanvas').addEventListener('click', () => {
    const canvasData = canvas.toDataURL('image/png');
    fetch('/generate-3d-from-canvas/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({ image: canvasData }),
    })
    .then((response) => response.json())
    .then((data) => {
        const outputImage = document.getElementById('outputImage');
        const outputPlaceholder = document.getElementById('outputPlaceholder');
        outputImage.src = data.generated_image_url;
        outputImage.classList.remove('d-none');
        outputPlaceholder.classList.add('d-none');
    });
});
