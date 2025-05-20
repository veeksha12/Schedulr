const API_URL = "http://127.0.0.1:8000/api";
// fix this code properly

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + localStorage.getItem("token")
  };
}

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

function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// Fetch logged-in user info and display it on dashboard
async function getUserInfo() {
  const res = await fetch(`${API_URL}/user/me`, { headers: authHeaders() });
  if (!res.ok) return null;
  const user = await res.json();
  return user;
}

// DASHBOARD INIT
if (window.location.pathname.includes("dashboard")) {
  getUserInfo().then(user => {
    if (user) {
      const userDisplay = document.getElementById("user-name");
      if (userDisplay) userDisplay.innerText = `Logged in as: ${user.username}`;
    }
  });
  loadProgress();
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
      <button onclick="selectCourse(${c.id}, '${c.name}')">View Exams</button>
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

// Tasks
async function fetchTodayTasks() {
  const res = await fetch(`${API_URL}/tasks/today`, { headers: authHeaders() });
  const tasks = await res.json();
  renderTasks(tasks);
}

async function addTask() {
  const taskInput = document.getElementById("new-task");
  const taskText = taskInput.value.trim();
  if (taskText === "") return;

  await fetch(`${API_URL}/tasks/?description=` + encodeURIComponent(taskText), {
    method: "POST",
    headers: authHeaders()
  });
  taskInput.value = "";
  fetchTodayTasks();
}

async function toggleTask(taskId, completed) {
  await fetch(`${API_URL}/tasks/${taskId}?completed=${completed}`, {
    method: "PUT",
    headers: authHeaders()
  });
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
  const res = await fetch(`${API_URL}/tasks/history`, { headers: authHeaders() });
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

// Grade Help & Chat API functions unchanged (omit for brevity)

// --- Planner CRUD ---
async function fetchPlanners() {
  const res = await fetch(`${API_URL}/planner/`, { headers: authHeaders() });
  const planners = await res.json();
  renderPlannerList(planners);
}

async function addPlanner() {
  const name = prompt("Planner name (e.g., Sem 5 – MSc):");
  if (!name) return;
  await fetch(`${API_URL}/planner/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name })
  });
  fetchPlanners();
}

function renderPlannerList(planners) {
  const box = document.getElementById("planner-box");
  box.innerHTML = "";
  planners.forEach(p => {
    const div = document.createElement("div");
    div.textContent = p.name;
    div.onclick = () => loadPlanner(p.id);
    box.appendChild(div);
  });
}

async function loadPlanner(plannerId) {
  // Example: Load courses for this planner (replace with your actual API if different)
  currentProgressId = plannerId;
  document.getElementById("current-progress-name").innerText = `Planner: ${plannerId}`;
  document.getElementById("course-section").style.display = "block";
  await loadCourses();
}

let currentCourseId = null;
let currentCourseName = "";

function selectCourse(id, name) {
  currentCourseId = id;
  currentCourseName = name;
  document.getElementById("current-course-name").innerText = name;
  document.getElementById("exam-section").style.display = "block";
  loadExams();
}

async function loadExams() {
  const res = await fetch(`${API_URL}/exams/course/${currentCourseId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    alert("Failed to load exams");
    return;
  }
  const exams = await res.json();
  renderExams(exams);
  calculateCurrentGrade(exams);
  getAIAdvice(exams);
}

function renderExams(exams) {
  const list = document.getElementById("exam-list");
  list.innerHTML = "";
  exams.forEach((exam) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <input type="text" value="${exam.name}" disabled />
      <input type="date" value="${exam.date}" disabled />
      <input type="number" value="${exam.marks}" min="0" max="100" onchange="updateExam(${exam.id}, 'marks', this.value)" />
      <input type="number" value="${exam.weightage}" min="0" max="100" onchange="updateExam(${exam.id}, 'weightage', this.value)" />
      <button onclick="removeExam(${exam.id})">Delete</button>
    `;
    list.appendChild(li);
  });
}

async function addExam() {
  const name = document.getElementById("exam-name").value.trim();
  const date = document.getElementById("exam-date").value;
  const marks = parseFloat(document.getElementById("exam-marks").value);
  const weightage = parseFloat(document.getElementById("exam-weightage").value);

  if (!name || !date || isNaN(marks) || isNaN(weightage)) {
    alert("Please fill all exam details correctly");
    return;
  }

  const res = await fetch(`${API_URL}/exams/course/${currentCourseId}`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ name, date, marks, weightage }),
  });

  if (!res.ok) {
    alert("Failed to add exam");
    return;
  }

  // Reset inputs
  document.getElementById("exam-name").value = "";
  document.getElementById("exam-date").value = "";
  document.getElementById("exam-marks").value = "";
  document.getElementById("exam-weightage").value = "";

  loadExams();
}

async function updateExam(examId, field, value) {
  const body = {};
  body[field] = field === "marks" || field === "weightage" ? parseFloat(value) : value;

  const res = await fetch(`${API_URL}/exams/${examId}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    alert("Failed to update exam");
    return;
  }
  loadExams();
}

async function removeExam(examId) {
  const res = await fetch(`${API_URL}/exams/${examId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (!res.ok) {
    alert("Failed to delete exam");
    return;
  }
  loadExams();
}

function calculateCurrentGrade(exams) {
  let totalWeightedMarks = 0;
  let totalWeight = 0;
  exams.forEach((exam) => {
    totalWeightedMarks += exam.marks * exam.weightage;
    totalWeight += exam.weightage;
  });
  const grade = totalWeight > 0 ? (totalWeightedMarks / totalWeight).toFixed(2) : "?";
  document.getElementById("calculated-grade").innerText = grade;
}

async function getAIAdvice(exams) {
  try {
    const res = await fetch(`${API_URL}/exams/ai/grade-help`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + localStorage.getItem("token") },
      body: JSON.stringify({ exams }),
    });
    const data = await res.json();
    alert("AI Advice: " + (data.response || data.error));
  } catch (err) {
    console.error("AI advice error", err);
  }
}

