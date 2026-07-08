/**
 * BDMS / IIMS - Interactive Client-Side Logic
 * Replicates government-portal dynamic behaviors and adds premium interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    initCustomCursor();
    initCollapsibleWidgets();
    initDragAndDropUploader();
    initCameraScanner();
});

/* ==========================================================================
   1. Special Interactive Cursor Trails (Canvas Particle Engine)
   ========================================================================== */
function initCustomCursor() {
    // Create cursor nodes
    const glow = document.createElement('div');
    glow.className = 'custom-cursor-glow';
    document.body.appendChild(glow);

    const dot = document.createElement('div');
    dot.className = 'custom-cursor-dot';
    document.body.appendChild(dot);

    // Create particles canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'cursor-canvas';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    // Resize canvas
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    let mouse = { x: -100, y: -100 };
    let glowPos = { x: -100, y: -100 };
    let particles = [];
    const colors = ['#ff9933', '#ffffff', '#128807']; // Indian Tricolour

    // Update mouse position
    window.addEventListener('mousemove', function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        
        // Instant position for internal dot
        dot.style.left = mouse.x + 'px';
        dot.style.top = mouse.y + 'px';

        // Spawn particles
        if (Math.random() < 0.3) {
            particles.push(new Particle(mouse.x, mouse.y));
        }
    });

    // Lagged smooth tracking for outer glow circle
    function updateGlow() {
        const dx = mouse.x - glowPos.x;
        const dy = mouse.y - glowPos.y;
        
        glowPos.x += dx * 0.15;
        glowPos.y += dy * 0.15;
        
        glow.style.left = glowPos.x + 'px';
        glow.style.top = glowPos.y + 'px';
        
        requestAnimationFrame(updateGlow);
    }
    updateGlow();

    // Particle constructor
    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 4 + 2;
            this.speedX = Math.random() * 2 - 1;
            this.speedY = Math.random() * 2 - 1;
            this.color = colors[Math.floor(Math.random() * colors.length)];
            this.alpha = 1.0;
            this.decay = Math.random() * 0.02 + 0.015;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.alpha -= this.decay;
        }

        draw() {
            ctx.save();
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 4;
            ctx.shadowColor = this.color;
            ctx.fill();
            ctx.restore();
        }
    }

    // Animation Loop
    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            
            if (particles[i].alpha <= 0) {
                particles.splice(i, 1);
                i--;
            }
        }
        
        requestAnimationFrame(animateParticles);
    }
    animateParticles();

    // Glow effects on interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .role-card, .material-sidebar-card, .file-upload-box, input, select, textarea');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            glow.style.width = '60px';
            glow.style.height = '60px';
            glow.style.borderColor = 'rgba(27, 94, 32, 0.8)'; // Green on hover
            glow.style.backgroundColor = 'rgba(27, 94, 32, 0.05)';
        });
        
        el.addEventListener('mouseleave', () => {
            glow.style.width = '40px';
            glow.style.height = '40px';
            glow.style.borderColor = 'rgba(230, 81, 0, 0.4)'; // Saffron back
            glow.style.backgroundColor = 'transparent';
        });
    });
}

/* ==========================================================================
   2. Collapsible Dashboard Sections
   ========================================================================== */
function initCollapsibleWidgets() {
    const collapsibles = document.querySelectorAll('.collapsible-title');
    collapsibles.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('i');
            
            if (content.style.display === 'none' || !content.style.display) {
                content.style.display = 'block';
                if (icon) {
                    icon.classList.remove('bi-chevron-down');
                    icon.classList.add('bi-chevron-up');
                }
            } else {
                content.style.display = 'none';
                if (icon) {
                    icon.classList.remove('bi-chevron-up');
                    icon.classList.add('bi-chevron-down');
                }
            }
        });
    });
}

/* ==========================================================================
   3. Drag-and-Drop Invoice PDF Uploader
   ========================================================================== */
function initDragAndDropUploader() {
    const uploadArea = document.querySelector('.file-upload-box');
    const fileInput = document.querySelector('.file-upload-box input[type="file"]');
    
    if (!uploadArea || !fileInput) return;

    // Trigger click on file input
    uploadArea.addEventListener('click', () => fileInput.click());

    // Highlight drop area
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        }, false);
    });

    // Drop handler
    uploadArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            updateFileNameDisplay(files[0].name);
        }
    });

    // Change handler
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            updateFileNameDisplay(this.files[0].name);
        }
    });

    function updateFileNameDisplay(name) {
        let nameDiv = document.getElementById('fileName');
        if (!nameDiv) {
            nameDiv = document.createElement('div');
            nameDiv.id = 'fileName';
            nameDiv.className = 'mt-3 text-success font-weight-bold';
            uploadArea.appendChild(nameDiv);
        }
        nameDiv.innerHTML = `<i class="bi bi-file-earmark-check-fill"></i> ✓ Selected: ${name}`;
    }
}

/* ==========================================================================
   4. Barcode Webcam Stream Capture (AJAX scanning)
   ========================================================================== */
function initCameraScanner() {
    const video = document.getElementById('scanner-video');
    const startBtn = document.getElementById('start-scanner-btn');
    const scanBar = document.querySelector('.scanner-laser-bar');
    const resultsContainer = document.getElementById('scanner-results-card');

    if (!video || !startBtn) return;

    let localStream = null;
    let scanInterval = null;

    startBtn.addEventListener('click', function() {
        if (localStream) {
            stopScanner();
            return;
        }

        startBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Initializing Camera...`;
        startBtn.disabled = true;

        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(function(stream) {
                video.srcObject = stream;
                localStream = stream;
                startBtn.innerHTML = `<i class="bi bi-camera-video-off"></i> Stop Camera`;
                startBtn.disabled = false;
                startBtn.classList.remove('btn-gov-primary');
                startBtn.classList.add('btn-gov-danger');
                if (scanBar) scanBar.style.display = 'block';

                // Start sending capture frames every 1.5 seconds for decoding
                scanInterval = setInterval(captureAndDecodeFrame, 1500);
            })
            .catch(function(err) {
                console.error("Camera access failed:", err);
                alert("Could not access camera: Make sure to grant permission or verify no other app is using it.");
                startBtn.innerHTML = `<i class="bi bi-camera-video"></i> Start Webcam`;
                startBtn.disabled = false;
            });
    });

    function stopScanner() {
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }
        if (video) video.srcObject = null;
        if (scanInterval) {
            clearInterval(scanInterval);
            scanInterval = null;
        }
        if (scanBar) scanBar.style.display = 'none';

        startBtn.innerHTML = `<i class="bi bi-camera-video"></i> Start Webcam`;
        startBtn.classList.remove('btn-gov-danger');
        startBtn.classList.add('btn-gov-primary');
    }

    function captureAndDecodeFrame() {
        if (!localStream) return;

        // Create virtual offscreen canvas to capture frame
        const tempCanvas = document.createElement('canvas');
        const width = video.videoWidth || 640;
        const height = video.videoHeight || 480;
        tempCanvas.width = width;
        tempCanvas.height = height;
        
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
        
        const base64Data = tempCanvas.toDataURL('image/png');

        // Send AJAX POST
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'canvas_data': base64Data
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Play notification beep sound if desired, and halt scanner
                stopScanner();
                renderScannerMatch(data);
            }
        })
        .catch(err => console.error("Scanner query failed:", err));
    }

    function renderScannerMatch(material) {
        if (!resultsContainer) return;

        resultsContainer.innerHTML = `
            <div class="card border-0 shadow-sm mt-4">
                <div class="card-header bg-success text-white d-flex align-items-center justify-content-between">
                    <h5 class="mb-0"><i class="bi bi-barcode"></i> Material Found!</h5>
                    <span class="badge bg-white text-success font-weight-bold">${material.barcode}</span>
                </div>
                <div class="card-body">
                    <h4 class="fw-bold mb-3" style="color: var(--primary-navy);">${material.material_name}</h4>
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <span class="text-muted d-block small font-weight-bold text-uppercase">Serial Number</span>
                            <strong>SR-${material.serial_number}</strong>
                        </div>
                        <div class="col-md-6 mb-2">
                            <span class="text-muted d-block small font-weight-bold text-uppercase">Vendor Receipt</span>
                            <strong>${material.vendor_name}</strong>
                        </div>
                        <div class="col-md-6 mb-2">
                            <span class="text-muted d-block small font-weight-bold text-uppercase">Date Received</span>
                            <strong>${material.date_received}</strong>
                        </div>
                        <div class="col-md-6 mb-2">
                            <span class="text-muted d-block small font-weight-bold text-uppercase">Available Quantity</span>
                            <span class="badge bg-success">${material.current_balance} units</span>
                        </div>
                    </div>
                    <div class="d-grid mt-4">
                        <a href="/material/${material.serial_number}/barcode/" class="btn btn-gov-primary">
                            <i class="bi bi-box-seam"></i> Open Material Workspace
                        </a>
                    </div>
                </div>
            </div>
        `;
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
}
