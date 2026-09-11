const featureList = document.getElementById('feature-list');
const activityList = document.getElementById('activity-list');
const motionStatus = document.getElementById('motion-status');
const lastPerson = document.getElementById('last-person');
const temperature = document.getElementById('temperature');
const humidity = document.getElementById('humidity');
const lastMotion = document.getElementById('last-motion');
const gasStatus = document.getElementById('gas-status');
const alertBox = document.getElementById('alert-box');
const fanButton = document.getElementById('fan-btn');
const lightButton = document.getElementById('light-btn');
const refreshButton = document.getElementById('refresh-btn');

const formatTime = (value) => {
  if (!value) return 'Not available';

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
};

const renderFeatures = (features = []) => {
  featureList.innerHTML = features
    .map((feature) => `<li>${feature}</li>`)
    .join('');
};

const renderActivities = (activities = []) => {
  if (!activities.length) {
    activityList.innerHTML = '<li>No activity recorded yet.</li>';
    return;
  }

  activityList.innerHTML = activities
    .map(
      (item) => `
        <li>
          <div>${item.message}</div>
          <span class="activity-time">${formatTime(item.time)}</span>
        </li>
      `,
    )
    .join('');
};

const updateControlButtons = (status) => {
  fanButton.textContent = `Fan: ${status.fan_on ? 'On' : 'Off'}`;
  lightButton.textContent = `Light: ${status.light_on ? 'On' : 'Off'}`;
  fanButton.classList.toggle('active', status.fan_on);
  lightButton.classList.toggle('active', status.light_on);
};

const renderStatus = (status) => {
  renderFeatures(status.features || []);
  renderActivities(status.recent_activity || []);

  motionStatus.textContent = status.motion_detected ? 'Detected' : 'Idle';
  lastPerson.textContent = status.last_person || 'Waiting...';
  temperature.textContent = status.temperature_c !== null ? `${status.temperature_c} °C` : 'No sensor';
  humidity.textContent = status.humidity !== null ? `${status.humidity} %` : 'No sensor';
  lastMotion.textContent = formatTime(status.last_motion_at);

  const gasAlert = status.gas_alarm;
  gasStatus.textContent = gasAlert ? 'Leak detected' : 'Normal';
  gasStatus.classList.toggle('alert', gasAlert);

  alertBox.textContent = gasAlert
    ? 'Gas leakage alert is active.'
    : 'No gas leakage detected.';

  alertBox.classList.toggle('safe', !gasAlert);
  alertBox.classList.toggle('alert', gasAlert);

  updateControlButtons(status);
};

const fetchStatus = async () => {
  const response = await fetch('/api/status');
  const status = await response.json();
  renderStatus(status);
};

const postControl = async (name, state) => {
  await fetch(`/api/control/${name}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ state }),
  });

  await fetchStatus();
};

fanButton.addEventListener('click', async () => {
  const nextState = fanButton.textContent.includes('On') ? false : true;
  await postControl('fan', nextState);
});

lightButton.addEventListener('click', async () => {
  const nextState = lightButton.textContent.includes('On') ? false : true;
  await postControl('light', nextState);
});

refreshButton.addEventListener('click', fetchStatus);

fetchStatus();
setInterval(fetchStatus, 3000);
