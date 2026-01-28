const townInput = document.getElementById("town");
const townStatus = document.getElementById("town-status");
const loadTownButton = document.getElementById("load-town");
const categorySlider = document.getElementById("category-slider");
const ownershipSlider = document.getElementById("ownership-slider");
const categoryValue = document.getElementById("category-value");
const ownershipValue = document.getElementById("ownership-value");
const spinButton = document.getElementById("spin");
const resultEl = document.getElementById("result");
const optionsList = document.getElementById("options-list");
const wheelCanvas = document.getElementById("wheel");
const ctx = wheelCanvas.getContext("2d");

const categoryMap = ["Fast Food", "Sit Down", "Food Truck", "All"];
const ownershipMap = ["Locally Owned", "Chain", "All"];
let currentOptions = [];
let currentRotation = 0;

function updateSliderLabels() {
  categoryValue.textContent = categoryMap[Number(categorySlider.value)];
  ownershipValue.textContent = ownershipMap[Number(ownershipSlider.value)];
}

function drawWheel() {
  const options = currentOptions.length ? currentOptions : [{ name: "Add options" }];
  const radius = wheelCanvas.width / 2;
  ctx.clearRect(0, 0, wheelCanvas.width, wheelCanvas.height);
  ctx.save();
  ctx.translate(radius, radius);
  ctx.rotate(currentRotation);

  const sliceAngle = (Math.PI * 2) / options.length;
  options.forEach((option, index) => {
    ctx.beginPath();
    ctx.fillStyle = index % 2 === 0 ? "#93c5fd" : "#dbeafe";
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, radius - 10, sliceAngle * index, sliceAngle * (index + 1));
    ctx.closePath();
    ctx.fill();

    ctx.save();
    ctx.rotate(sliceAngle * index + sliceAngle / 2);
    ctx.textAlign = "right";
    ctx.fillStyle = "#1e293b";
    ctx.font = "bold 14px sans-serif";
    ctx.fillText(option.name, radius - 24, 8);
    ctx.restore();
  });

  ctx.restore();
}

function renderOptions() {
  optionsList.innerHTML = "";
  if (!currentOptions.length) {
    const li = document.createElement("li");
    li.textContent = "No options found for this town yet.";
    optionsList.appendChild(li);
    drawWheel();
    return;
  }

  currentOptions.forEach((option) => {
    const li = document.createElement("li");
    li.textContent = `${option.name} · ${option.category} · ${option.ownership}`;
    optionsList.appendChild(li);
  });
  drawWheel();
}

async function loadTown() {
  const town = townInput.value.trim();
  if (!town) {
    return;
  }
  townStatus.textContent = "Loading...";
  const response = await fetch(`/api/options?town=${encodeURIComponent(town)}`);
  const data = await response.json();
  currentOptions = data.options || [];
  renderOptions();
  townStatus.textContent = currentOptions.length
    ? `Loaded ${currentOptions.length} options for ${data.town}.`
    : `No saved options for ${data.town} yet.`;
}

async function spinWheel() {
  const town = townInput.value.trim();
  if (!town) {
    return;
  }

  const payload = {
    town,
    category: categoryMap[Number(categorySlider.value)],
    ownership: ownershipMap[Number(ownershipSlider.value)],
  };

  const response = await fetch("/api/spin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    resultEl.textContent = "No matches for those filters.";
    return;
  }

  const data = await response.json();
  const chosen = data.result;
  resultEl.textContent = `You should try: ${chosen.name}`;

  const options = currentOptions.length ? currentOptions : [chosen];
  const chosenIndex = options.findIndex((option) => option.name === chosen.name);
  const sliceAngle = (Math.PI * 2) / options.length;
  const rotations = 6;
  const targetAngle = (options.length - chosenIndex) * sliceAngle;

  const start = currentRotation;
  const end = rotations * Math.PI * 2 + targetAngle;
  const duration = 1600;
  const startTime = performance.now();

  function animate(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    currentRotation = start + (end - start) * eased;
    drawWheel();
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }

  requestAnimationFrame(animate);
}

categorySlider.addEventListener("input", updateSliderLabels);
ownershipSlider.addEventListener("input", updateSliderLabels);
loadTownButton.addEventListener("click", loadTown);
spinButton.addEventListener("click", spinWheel);

updateSliderLabels();
loadTown();
