/**
 * FoodWaste AI - Frontend Controller
 * Handles image upload, webcam capture, benchmark presets, canvas overlays, and API calls.
 */

let currentImageId = null;
let currentWebcamStream = null;

// Category colors matching backend
const CATEGORY_COLORS = {
  "Organic": "#2ecc71",
  "Recyclable": "#3498db",
  "Glass": "#1abc9c",
  "E-Waste": "#e74c3c",
  "Other": "#95a5a6"
};

// Preset images mapping
const PRESET_IMAGE_URLS = {
  "case1": "/static/samples/case1_banana.jpg",
  "case2": "/static/samples/case2_recyclables.jpg",
  "case3": "/static/samples/case3_mixed.jpg",
  "case4": "/static/samples/case4_uncertain.jpg",
  "case5": "/static/samples/case5_unknown.jpg",
  "odisha_canteen": "/static/samples/odisha_canteen.jpg"
};

document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  fetchRecentLogs();
  checkBackendHealth();
});

// Health check
async function checkBackendHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    const statusEl = document.getElementById("engine-status");
    if (data.status === "OK") {
      statusEl.textContent = `Online (${data.mode})`;
    }
  } catch (err) {
    document.getElementById("engine-status").textContent = "Backend Offline";
  }
}

// Tab Switching
function switchInputTab(tab) {
  const uploadPanel = document.getElementById("upload-panel");
  const cameraPanel = document.getElementById("camera-panel");
  const uploadBtn = document.getElementById("tab-upload-btn");
  const cameraBtn = document.getElementById("tab-camera-btn");

  if (tab === "upload") {
    uploadPanel.classList.remove("hidden");
    cameraPanel.classList.add("hidden");
    uploadBtn.classList.add("active");
    cameraBtn.classList.remove("active");
    stopWebcam();
  } else {
    uploadPanel.classList.add("hidden");
    cameraPanel.classList.remove("hidden");
    uploadBtn.classList.remove("active");
    cameraBtn.classList.add("active");
    startWebcam();
  }
}

// Webcam handlers
async function startWebcam() {
  const video = document.getElementById("webcam-video");
  try {
    currentWebcamStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    video.srcObject = currentWebcamStream;
  } catch (err) {
    console.error("Camera access failed:", err);
    alert("Camera permission denied or camera device not found. You can still use Image Upload or Hackathon Presets.");
    switchInputTab("upload");
  }
}

function stopWebcam() {
  if (currentWebcamStream) {
    currentWebcamStream.getTracks().forEach(track => track.stop());
    currentWebcamStream = null;
  }
}

function captureWebcamSnapshot() {
  const video = document.getElementById("webcam-video");
  if (!video.videoWidth) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    const file = new File([blob], "camera_snapshot.jpg", { type: "image/jpeg" });
    processImageUpload(file);
    switchInputTab("upload");
  }, "image/jpeg", 0.9);
}

// Drag & Drop
function setupDragAndDrop() {
  const dropZone = document.getElementById("drop-zone");

  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
      e.preventDefault();
      dropZone.style.borderColor = "#10b981";
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
      e.preventDefault();
      dropZone.style.borderColor = "rgba(255, 255, 255, 0.12)";
    });
  });

  dropZone.addEventListener("drop", e => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      processImageUpload(files[0]);
    }
  });
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    processImageUpload(file);
  }
}

// Process Image Upload
async function processImageUpload(file) {
  showLoading();
  const startTime = performance.now();

  const formData = new FormData();
  formData.append("image", file);

  try {
    const res = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Inference failed.");
    const data = await res.json();
    const latency = Math.round(performance.now() - startTime);

    renderPipelineResults(data, latency);
  } catch (err) {
    alert("Error processing image: " + err.message);
  }
}

// Benchmark Preset Loader
async function loadBenchmarkPreset(presetName) {
  showLoading();
  const startTime = performance.now();

  // Highlight selected button
  document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active-highlight"));
  const clickedBtn = event?.currentTarget;
  if (clickedBtn) clickedBtn.classList.add("active-highlight");

  const imageUrl = PRESET_IMAGE_URLS[presetName];
  try {
    // Fetch preset image as blob
    const imgRes = await fetch(imageUrl);
    const blob = await imgRes.blob();
    const file = new File([blob], `${presetName}.jpg`, { type: "image/jpeg" });

    const formData = new FormData();
    formData.append("image", file);
    formData.append("preset_mode", presetName);

    const res = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Inference failed.");
    const data = await res.json();
    const latency = Math.round(performance.now() - startTime);

    renderPipelineResults(data, latency);
  } catch (err) {
    console.error("Preset error:", err);
    alert("Could not load preset: " + err.message);
  }
}

// Render Results to UI
function renderPipelineResults(data, latency) {
  currentImageId = data.image_id;

  // 1. Update visualizer
  const emptyState = document.getElementById("empty-state");
  const resultImg = document.getElementById("annotated-result-img");
  const previewCanvas = document.getElementById("preview-canvas");

  emptyState.style.display = "none";
  previewCanvas.style.display = "none";
  resultImg.classList.remove("hidden");
  resultImg.src = data.annotated_image;

  document.getElementById("detected-count-badge").textContent = `${data.objects_detected} Object(s) Detected`;
  document.getElementById("detection-speed-badge").textContent = `⚡ Inference Latency: ${latency}ms`;

  // 2. Update Status Banner
  const banner = document.getElementById("status-banner");
  const bannerTitle = document.getElementById("banner-title");
  const bannerRec = document.getElementById("banner-recommendation");
  const bannerIcon = document.getElementById("banner-icon");

  banner.className = "status-banner"; // reset

  if (data.status === "Mixed Waste") {
    banner.classList.add("banner-mixed");
    bannerIcon.textContent = "⚠️";
    bannerTitle.textContent = "MIXED WASTE DETECTED";
  } else if (data.status === "Uncertain") {
    banner.classList.add("banner-uncertain");
    bannerIcon.textContent = "❓";
    bannerTitle.textContent = "MANUAL VERIFICATION REQUIRED";
  } else if (data.status === "Special Handling Required") {
    banner.classList.add("banner-special");
    bannerIcon.textContent = "📦";
    bannerTitle.textContent = "UNKNOWN WASTE DETECTED";
  } else {
    banner.classList.add("banner-single");
    bannerIcon.textContent = "✅";
    bannerTitle.textContent = `${data.status.toUpperCase()}`;
  }

  bannerRec.textContent = data.recommendation;

  // 3. Update Designated Bins
  const binContainer = document.getElementById("bin-routing-container");
  binContainer.innerHTML = "";
  if (data.bin_guidance && data.bin_guidance.length > 0) {
    data.bin_guidance.forEach(bin => {
      const card = document.createElement("div");
      card.className = "bin-card";
      card.style.borderLeftColor = bin.color;

      card.innerHTML = `
        <div class="bin-card-header">
          <span class="bin-name">${bin.bin_name}</span>
          <span class="bin-cat-tag" style="background:${bin.color}">${bin.category}</span>
        </div>
        <div class="bin-tip">${bin.handling_tip}</div>
      `;
      binContainer.appendChild(card);
    });
  } else {
    binContainer.innerHTML = `<div class="bin-empty">No specific bins designated.</div>`;
  }

  // 4. Update Objects List Breakdown
  const objectsList = document.getElementById("objects-list");
  objectsList.innerHTML = "";

  if (data.objects && data.objects.length > 0) {
    data.objects.forEach(obj => {
      const catColor = CATEGORY_COLORS[obj.category] || "#95a5a6";
      const confPct = Math.round(obj.confidence * 100);

      const item = document.createElement("div");
      item.className = "object-item";
      item.innerHTML = `
        <div class="obj-info">
          <div class="obj-bullet" style="background:${catColor}"></div>
          <div>
            <div class="obj-name">${obj.object.replace(/_/g, ' ')}</div>
            <div class="obj-cat">${obj.category} Waste</div>
          </div>
        </div>
        <div class="obj-metric">
          <div class="conf-bar-bg">
            <div class="conf-bar-fill" style="width:${confPct}%; background:${catColor}"></div>
          </div>
          <span class="conf-val">${confPct}%</span>
        </div>
      `;
      objectsList.appendChild(item);
    });
  } else {
    objectsList.innerHTML = `<p class="placeholder-text">No objects isolated.</p>`;
  }

  // 5. Update confidence summary
  const summaryEl = document.getElementById("confidence-summary-text");
  if (data.confidence_summary && data.confidence_summary.avg_confidence) {
    summaryEl.textContent = `Avg Conf: ${(data.confidence_summary.avg_confidence * 100).toFixed(1)}%`;
  } else {
    summaryEl.textContent = "";
  }

  // 6. Enable Feedback Section
  const feedbackSection = document.getElementById("feedback-section");
  feedbackSection.style.display = "block";
  document.getElementById("feedback-acknowledgment").textContent = "";

  // 7. Refresh audit trail table
  fetchRecentLogs();
}

function showLoading() {
  document.getElementById("detected-count-badge").textContent = "Processing Multi-Object Detection...";
  document.getElementById("detection-speed-badge").textContent = "Running YOLO & Decision Pipeline...";
}

// Feedback submission
async function submitUserFeedback(isCorrect) {
  if (!currentImageId) return;

  const ack = document.getElementById("feedback-acknowledgment");
  ack.textContent = "Logging active-learning verification...";

  try {
    const res = await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_id: currentImageId,
        prediction_correct: isCorrect,
        user_correction: isCorrect ? null : "User flagged edge-case for retraining",
        notes: isCorrect ? "Confirmed accurate by user" : "Inaccurate detection/decision"
      })
    });

    if (res.ok) {
      ack.textContent = isCorrect 
        ? "✓ Thank you! Marked as verified sample." 
        : "⚠️ Logged as difficult example for dataset retraining.";
    }
  } catch (err) {
    ack.textContent = "Could not record feedback.";
  }
}

// Fetch and render recent audit records
async function fetchRecentLogs() {
  try {
    const res = await fetch("/history?limit=10");
    const data = await res.json();
    const tbody = document.getElementById("audit-table-body");

    if (!data.history || data.history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty">No prediction records logged yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    data.history.forEach(row => {
      const tr = document.createElement("tr");
      const dateStr = new Date(row.timestamp).toLocaleTimeString();
      const statusClass = row.final_status.includes("Mixed") ? "color:#f87171;font-weight:700" : "color:#34d399";
      
      const cats = Array.isArray(row.objects) ? [...new Set(row.objects.map(o => o.category))].join(", ") : "-";

      tr.innerHTML = `
        <td style="font-family:var(--font-mono);font-size:12px">${dateStr}</td>
        <td><span style="${statusClass}">${row.final_status}</span></td>
        <td><strong>${row.objects_detected}</strong> item(s)</td>
        <td>${cats}</td>
        <td style="max-width:300px;font-size:12px">${row.recommendation}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Could not fetch logs:", err);
  }
}

// ==========================================
// NEW HACKATHON ENHANCEMENTS
// ==========================================

let lastPredictionPayload = null;

// Hook payload save into renderPipelineResults
const originalRenderPipelineResults = renderPipelineResults;
renderPipelineResults = function(data, latency) {
  lastPredictionPayload = data;
  originalRenderPipelineResults(data, latency);
  // Update JSON viewer if active
  const pre = document.querySelector("#json-viewer-pre code");
  if (pre) {
    // Exclude bulky base64 from preview for clean inspector readability
    const previewData = { ...data };
    if (previewData.annotated_image) {
      previewData.annotated_image = "[base64 image stream omitted for display]";
    }
    pre.textContent = JSON.stringify(previewData, null, 2);
  }
};

function toggleJsonViewer() {
  const container = document.getElementById("json-viewer-container");
  if (container.classList.contains("hidden")) {
    container.classList.remove("hidden");
    if (!lastPredictionPayload) {
      document.querySelector("#json-viewer-pre code").textContent = "No prediction ran yet. Select a benchmark or upload an image.";
    }
  } else {
    container.classList.add("hidden");
  }
}

function copyJsonPayload() {
  if (!lastPredictionPayload) {
    alert("No prediction data to copy.");
    return;
  }
  navigator.clipboard.writeText(JSON.stringify(lastPredictionPayload, null, 2))
    .then(() => alert("API JSON payload copied to clipboard!"))
    .catch(() => alert("Could not copy to clipboard."));
}

// Export Audit Logs
function exportAuditLogs(format) {
  window.open(`/api/export?format=${format}`, "_blank");
}

// Modal Controllers
function openMetricsModal() {
  document.getElementById("metrics-modal").classList.remove("hidden");
}

function closeMetricsModal(e) {
  if (e && e.target !== document.getElementById("metrics-modal") && !e.target.classList.contains("modal-close-btn")) {
    return;
  }
  document.getElementById("metrics-modal").classList.add("hidden");
}

function openSandboxModal() {
  document.getElementById("sandbox-modal").classList.remove("hidden");
}

function closeSandboxModal(e) {
  if (e && e.target !== document.getElementById("sandbox-modal") && !e.target.classList.contains("modal-close-btn")) {
    return;
  }
  document.getElementById("sandbox-modal").classList.add("hidden");
}

// Sandbox Staging State
let stagedSandboxItems = [];

function syncSandboxCustomInput() {
  const select = document.getElementById("sandbox-obj-select");
  const customInput = document.getElementById("sandbox-custom-name");
  if (select.value === "custom") {
    customInput.classList.remove("hidden");
    customInput.focus();
  } else {
    customInput.classList.add("hidden");
  }
}

function addSandboxItem() {
  const select = document.getElementById("sandbox-obj-select");
  const customInput = document.getElementById("sandbox-custom-name");
  const catSelect = document.getElementById("sandbox-cat-select");
  const slider = document.getElementById("sandbox-conf-slider");

  let objName = select.value === "custom" ? customInput.value.trim() : select.value;
  if (!objName) {
    alert("Please enter an object name.");
    return;
  }

  const confidence = parseFloat(slider.value);
  const category = catSelect.value || null;

  stagedSandboxItems.push({
    object: objName,
    category: category,
    confidence: confidence
  });

  renderStagedSandbox();
  if (select.value === "custom") customInput.value = "";
}

function removeSandboxItem(index) {
  stagedSandboxItems.splice(index, 1);
  renderStagedSandbox();
}

function clearSandboxItems() {
  stagedSandboxItems = [];
  renderStagedSandbox();
  document.getElementById("sandbox-result-box").classList.add("hidden");
}

function renderStagedSandbox() {
  const container = document.getElementById("staged-items-container");
  const countEl = document.getElementById("staged-count");
  countEl.textContent = stagedSandboxItems.length;

  if (stagedSandboxItems.length === 0) {
    container.innerHTML = `<p class="placeholder-text">Add objects above to simulate a custom multi-object waste scenario.</p>`;
    return;
  }

  container.innerHTML = "";
  stagedSandboxItems.forEach((item, idx) => {
    const chip = document.createElement("div");
    chip.className = "staged-chip";
    chip.innerHTML = `
      <div class="chip-meta">
        <strong>${item.object.replace(/_/g, ' ')}</strong>
        <span style="color:#10b981;font-family:var(--font-mono)">${Math.round(item.confidence * 100)}%</span>
        ${item.category ? `<span style="font-size:10px;background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;">${item.category}</span>` : ''}
      </div>
      <span class="chip-del" onclick="removeSandboxItem(${idx})">✕</span>
    `;
    container.appendChild(chip);
  });
}

async function executeSandboxDecision() {
  if (stagedSandboxItems.length === 0) {
    alert("Please stage at least one waste item first.");
    return;
  }

  const btn = document.querySelector(".execute-sandbox-btn");
  btn.textContent = "Running AI Decision Engine...";

  try {
    const res = await fetch("/decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objects: stagedSandboxItems })
    });

    if (!res.ok) throw new Error("Decision Engine call failed.");
    const data = await res.json();

    const resultBox = document.getElementById("sandbox-result-box");
    resultBox.classList.remove("hidden");

    const statusBadge = document.getElementById("sandbox-res-status");
    statusBadge.textContent = data.status;
    if (data.status.includes("Mixed")) {
      statusBadge.style.color = "#f87171";
      statusBadge.style.background = "rgba(239, 68, 68, 0.15)";
      statusBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
    } else {
      statusBadge.style.color = "#34d399";
      statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
      statusBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
    }

    document.getElementById("sandbox-res-action").textContent = data.action_type;
    document.getElementById("sandbox-res-rec").textContent = data.recommendation;
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    btn.textContent = "⚡ Evaluate with Decision Engine";
  }
}

// ==========================================
// VERNACULAR & VOICE NARRATION CONTROLLER
// ==========================================
let currentLanguage = "en";

function setLanguage(lang) {
  currentLanguage = lang;
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
  const activeBtn = document.getElementById(`lang-btn-${lang}`);
  if (activeBtn) activeBtn.classList.add("active");

  // If a prediction is active, update banner recommendation text immediately
  if (lastPredictionPayload && lastPredictionPayload.multilingual_guidance) {
    const text = lastPredictionPayload.multilingual_guidance[lang] || lastPredictionPayload.recommendation;
    document.getElementById("banner-recommendation").textContent = text;
  }
}

function playVoiceNarration() {
  if (!('speechSynthesis' in window)) {
    alert("Speech Synthesis is not supported in this browser.");
    return;
  }

  let textToSpeak = document.getElementById("banner-recommendation").textContent;
  if (!textToSpeak || textToSpeak.includes("Awaiting Waste")) {
    textToSpeak = "Please upload or scan an image first to run waste segregation.";
  }

  window.speechSynthesis.cancel(); // Stop any previous speech
  const utterance = new SpeechSynthesisUtterance(textToSpeak);

  // Set voice accent
  if (currentLanguage === "hi") {
    utterance.lang = "hi-IN";
  } else if (currentLanguage === "or") {
    utterance.lang = "hi-IN"; // Hindi fallback for Odia phonetics if or-IN is absent
  } else {
    utterance.lang = "en-IN";
  }

  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

// ==========================================
// ESG & SMART BIN TWIN RENDER ENHANCEMENT
// ==========================================
const prevRenderPipelineResults = renderPipelineResults;
renderPipelineResults = function(data, latency) {
  prevRenderPipelineResults(data, latency);

  // 1. Update ESG Impact Widget
  if (data.esg_impact) {
    const esg = data.esg_impact;
    document.getElementById("esg-co2").textContent = `${esg.co2e_prevented_kg} kg`;
    document.getElementById("esg-water").textContent = `${esg.water_conserved_liters} L`;
    document.getElementById("esg-diversion").textContent = `${esg.diversion_rate_pct}%`;
    document.getElementById("esg-grade-badge").textContent = `Grade ${esg.esg_grade}`;
  }

  // 2. Update Virtual Smart Bin IoT Digital Twin
  updateSmartBinTwin(data);

  // 3. Update Vernacular banner text based on selected language
  if (data.multilingual_guidance && data.multilingual_guidance[currentLanguage]) {
    document.getElementById("banner-recommendation").textContent = data.multilingual_guidance[currentLanguage];
  }
};

function updateSmartBinTwin(data) {
  const servoPill = document.getElementById("iot-servo-status");
  const flapOrganic = document.getElementById("flap-organic");
  const flapRecyclable = document.getElementById("flap-recyclable");
  const flapGlass = document.getElementById("flap-glass");
  const flapEwaste = document.getElementById("flap-ewaste");

  // Reset flaps
  [flapOrganic, flapRecyclable, flapGlass, flapEwaste].forEach(f => {
    f.textContent = "LOCKED";
    f.classList.remove("flap-open");
  });

  if (data.status === "Mixed Waste") {
    servoPill.textContent = "FLAPS LOCKED (Mix Alert)";
    servoPill.style.color = "#f87171";
    servoPill.style.borderColor = "rgba(239, 68, 68, 0.4)";
    servoPill.style.background = "rgba(239, 68, 68, 0.12)";
  } else {
    servoPill.textContent = "Routing Active";
    servoPill.style.color = "#34d399";
    servoPill.style.borderColor = "rgba(16, 185, 129, 0.4)";
    servoPill.style.background = "rgba(16, 185, 129, 0.12)";

    const cats = data.categories || [];
    if (cats.includes("Organic")) {
      flapOrganic.textContent = "OPEN";
      flapOrganic.classList.add("flap-open");
    }
    if (cats.includes("Recyclable")) {
      flapRecyclable.textContent = "OPEN";
      flapRecyclable.classList.add("flap-open");
    }
    if (cats.includes("Glass")) {
      flapGlass.textContent = "OPEN";
      flapGlass.classList.add("flap-open");
    }
    if (cats.includes("E-Waste")) {
      flapEwaste.textContent = "OPEN";
      flapEwaste.classList.add("flap-open");
    }
  }
}

// ==========================================
// CONTINUOUS SCAN MODE CONTROLLER
// ==========================================
let continuousScanTimer = null;

function toggleContinuousScan() {
  const chk = document.getElementById("continuous-scan-chk");
  if (chk.checked) {
    if (!currentWebcamStream) {
      alert("Please ensure the camera is active first.");
      chk.checked = false;
      return;
    }
    document.getElementById("detection-speed-badge").textContent = "⚡ Continuous Radar Active";
    continuousScanTimer = setInterval(() => {
      const video = document.getElementById("webcam-video");
      if (video && video.videoWidth > 0) {
        captureWebcamSnapshot();
      }
    }, 1800);
  } else {
    if (continuousScanTimer) {
      clearInterval(continuousScanTimer);
      continuousScanTimer = null;
    }
    document.getElementById("detection-speed-badge").textContent = "⚡ Realtime Latency: <50ms";
  }
}


