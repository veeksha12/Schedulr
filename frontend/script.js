const API_URL = "http://127.0.0.1:8000/api";
let token = localStorage.getItem("token");

// LOGIN
async function login() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();
  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    window.location.href = "dashboard.html";
  } else {
    alert("Login failed");
  }
}

// SIGNUP
async function signup() {
  const username = document.getElementById("signup-username").value;
  const password = document.getElementById("signup-password").value;
  const res = await fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (res.ok) {
    alert("Signup successful. You can now log in.");
  } else {
    alert("Signup failed");
  }
}

// DASHBOARD.JS LOGIC ONLY
if (window.location.pathname.includes("dashboard")) {
  loadProgress();
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// Create Progress
async function createProgress() {
  const name = document.getElementById("progress-name").value;
  const description = document.getElementById("progress-desc").value;
  await fetch(`${API_URL}/progress/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name, description })
  });
  loadProgress();
}

// Load Progress Profiles
async function loadProgress() {
  const res = await fetch(`${API_URL}/progress/`, { headers: authHeaders() });
  const progressList = await res.json();
  const container = document.getElementById("progress-list");
  container.innerHTML = "";
  progressList.forEach(p => {
    const div = document.createElement("div");
    div.innerHTML = `
      <strong>${p.name}</strong> - ${p.description}
      <button onclick="selectProgress(${p.id}, '${p.name}')">View Courses</button>
    `;
    container.appendChild(div);
  });
}

// Select Progress
let currentProgressId = null;
function selectProgress(id, name) {
  currentProgressId = id;
  document.getElementById("current-progress-name").innerText = name;
  document.getElementById("course-section").style.display = "block";
  loadCourses();
}

// Add Course
async function addCourse() {
  const name = document.getElementById("course-name").value;
  const target_grade = parseFloat(document.getElementById("target-grade").value);
  const free_hours = parseFloat(document.getElementById("free-hours").value);
  await fetch(`${API_URL}/progress/${currentProgressId}/courses`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name, target_grade, free_hours_per_day: free_hours })
  });
  loadCourses();
}

// Load Courses
async function loadCourses() {
  const res = await fetch(`${API_URL}/progress/${currentProgressId}/courses`, {
    headers: authHeaders()
  });
  const courses = await res.json();
  const container = document.getElementById("course-list");
  container.innerHTML = "";
  courses.forEach(c => {
    const div = document.createElement("div");
    div.innerHTML = `
      <p><strong>${c.name}</strong> — Grade: ${c.current_grade ?? "?"} | Target: ${c.target_grade}</p>
      <button onclick="autoGrade(${c.id})">Auto Update Grade</button>
    `;
    container.appendChild(div);
  });
}

// Trigger Sonar API
async function autoGrade(courseId) {
  const res = await fetch(`${API_URL}/course/${courseId}/autograde`, {
    method: "POST",
    headers: authHeaders()
  });
  const result = await res.json();
  alert("Updated Grade: " + result.updated_grade);
  loadCourses();
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + localStorage.getItem("token")
  };
}

async function fetchTodayTasks() {
  const res = await fetch("/tasks/today");
  const tasks = await res.json();
  renderTasks(tasks);
}

async function addTask() {
  const taskInput = document.getElementById("new-task");
  const taskText = taskInput.value.trim();
  if (taskText === "") return;

  await fetch("/tasks/?description=" + encodeURIComponent(taskText), { method: "POST" });
  taskInput.value = "";
  fetchTodayTasks();
}

async function toggleTask(taskId, completed) {
  await fetch(`/tasks/${taskId}?completed=${completed}`, { method: "PUT" });
  fetchTodayTasks();
}

function renderTasks(tasks) {
  const taskList = document.getElementById("task-list");
  taskList.innerHTML = "";
  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = task.completed ? "completed" : "";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.completed;
    checkbox.onchange = () => toggleTask(task.id, checkbox.checked);

    const span = document.createElement("span");
    span.textContent = task.description;

    li.appendChild(checkbox);
    li.appendChild(span);
    taskList.appendChild(li);
  }
}

async function fetchTaskHistory() {
  const res = await fetch("/tasks/history");
  const history = await res.json();
  const list = document.getElementById("task-history");
  list.innerHTML = "";
  history.forEach(task => {
    const li = document.createElement("li");
    li.textContent = `[${task.date}] ${task.completed ? "✔️" : "❌"} ${task.description}`;
    list.appendChild(li);
  });
}

window.onload = () => {
  fetchTodayTasks();
  fetchTaskHistory();
};
