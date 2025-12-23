const nameText = "Hello, I'm AYUSHMAN KAR";
let i = 0;
let isDeleting = false;
function typeEffect() {
  const element = document.getElementById("type-name");
  if (isDeleting) {
    element.textContent = nameText.substring(0, i - 1);
    i--;
  } else {
    element.textContent = nameText.substring(0, i + 1);
    i++;
  }
  let typeSpeed = isDeleting ? 60 : 120;
  if (!isDeleting && i === nameText.length) {
    isDeleting = true;
    typeSpeed = 1500;
  } else if (isDeleting && i === 0) {
    isDeleting = false;
    typeSpeed = 500;
  }
  setTimeout(typeEffect, typeSpeed);
}
window.addEventListener("load", typeEffect);
const roles = [
  "Full Stack Developer",
  "Backend Engineer",
  "Deep Learning Enthusiast",
  "Computer Vision Learner",
  "UI/UX Enthusiast",
  "NLP Specialist",
  "AI/ML Explorer",
];

let roleIndex = 0;
const roleEl = document.getElementById("job-rotate");

function rotateRole() {
  roleEl.style.opacity = 0;

  setTimeout(() => {
    roleEl.textContent = roles[roleIndex];
    roleEl.style.opacity = 1;
    roleIndex = (roleIndex + 1) % roles.length;
  }, 300);
}

rotateRole();
setInterval(rotateRole, 2500);
function Effect() {
  const element = document.getElementById("name"); //
  const currentText = isDeleting
    ? nameText.substring(0, i - 1)
    : nameText.substring(0, i + 1);

  element.textContent = currentText;

  // Update the data-text attribute for the glitch effect to work
  element.setAttribute("data-text", currentText);

  if (isDeleting) i--;
  else i++;

  let typeSpeed = isDeleting ? 60 : 120;

  if (!isDeleting && i === nameText.length) {
    isDeleting = true;
    typeSpeed = 1500;
  } else if (isDeleting && i === 0) {
    isDeleting = false;
    typeSpeed = 500;
  }

  setTimeout(Effect, typeSpeed); //
}
/* MOBILE MENU */
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger?.addEventListener("click", () => {
  navMenu.classList.toggle("active");
});

/* SMOOTH SCROLL */
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (e) => {
    e.preventDefault();
    document
      .querySelector(anchor.getAttribute("href"))
      .scrollIntoView({ behavior: "smooth" });
  });
});

/* FLIP CARDS (CLICK FOR MOBILE) */
document.querySelectorAll(".skill-card").forEach((card) => {
  card.addEventListener("click", () => {
    card.classList.toggle("active");
  });
});

/* FETCH PROJECTS */
async function loadProjects() {
  try {
    const res = await fetch("/api/projects");
    const data = await res.json();
    const grid = document.getElementById("projectsGrid");

    if (!data.projects || data.projects.length === 0) {
      grid.innerHTML = `
        <div class="project-card" onclick="openProjectModal(
            'AI Crop Recommendation System',
            '/static/projects/crop-ai.jpg',
            'A smart ML-based system that recommends crops based on soil nutrients, weather, and location.',
            'https://github.com/yourusername/crop-ai',
            '#'
        )">
            <img src="/static/projects/crop-ai.jpg">
            <h3>AI Crop Recommendation System</h3>
            <p>ML-powered crop recommendation platform.</p>
            <div class="project-actions">
                <a href="https://github.com/yourusername/crop-ai" target="_blank">GitHub</a>
                <a href="#" target="_blank">Live</a>
            </div>
        </div>

        <div class="project-card" onclick="openProjectModal(
            'Society Management System',
            '/static/projects/society.jpg',
            'A full-stack society management system with admin and member roles.',
            'https://github.com/yourusername/society-management',
            '#'
        )">
            <img src="/static/projects/society.jpg">
            <h3>Society Management System</h3>
            <p>Role-based society management platform.</p>
            <div class="project-actions">
                <a href="https://github.com/yourusername/society-management" target="_blank">GitHub</a>
                <a href="#" target="_blank">Live</a>
            </div>
        </div>

        <div class="project-card" onclick="openProjectModal(
            'Personal Portfolio Website',
            '/static/projects/portfolio.jpg',
            'Animated portfolio with admin dashboard, messaging & SMTP email notifications.',
            'https://github.com/yourusername/portfolio',
            '#'
        )">
            <img src="/static/projects/portfolio.jpg">
            <h3>Personal Portfolio Website</h3>
            <p>Modern animated portfolio website.</p>
            <div class="project-actions">
                <a href="https://github.com/yourusername/portfolio" target="_blank">GitHub</a>
                <a href="#" target="_blank">Live</a>
            </div>
        </div>
    `;
      return;
    }

    grid.innerHTML = data.projects
      .map(
        (p) => `
            <div class="project-card">
                <h3>${p.title}</h3>
                <p>${p.description}</p>
                <div class="skills">
                    ${p.technologies
                      .split(",")
                      .map((t) => `<span class="skill-tag">${t.trim()}</span>`)
                      .join("")}
                </div>
            </div>
        `
      )
      .join("");
  } catch (e) {
    console.error(e);
  }
}
loadProjects();

/* CONTACT FORM */
const form = document.getElementById("contactForm");
const msg = document.getElementById("formMessage");

form?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    name: name.value,
    email: email.value,
    message: message.value,
  };

  try {
    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const out = await res.json();
    msg.style.display = "block";
    msg.textContent = out.message || "Error";
    form.reset();
  } catch {
    msg.style.display = "block";
    msg.textContent = "Network error";
  }
});
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  },
  { threshold: 0.2 }
);

document.querySelectorAll(".reveal").forEach((el) => {
  revealObserver.observe(el);
});
function openProjectModal(title, image, desc, github, live) {
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalImage").src = image;
  document.getElementById("modalDesc").textContent = desc;
  document.getElementById("modalGithub").href = github;
  document.getElementById("modalLive").href = live;

  document.getElementById("projectModal").classList.add("show");
}

function closeProjectModal() {
  document.getElementById("projectModal").classList.remove("show");
}
async function login() {
  const res = await fetch("/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username.value,
      password: password.value,
    }),
  });

  if (res.ok) {
    window.location.href = "/admin/dashboard";
  } else {
    alert("Invalid credentials");
  }
}
/* =========================
   TOAST NOTIFICATION
========================= */
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2500);
}

/* =========================
   PROJECTS SECTION
========================= */
async function loadAdminProjects() {
  const res = await fetch("/admin/project");
  const projects = await res.json();

  const container = document.getElementById("adminProjects");
  container.innerHTML = projects
    .map(
      (p) => `
        <div class="admin-project">
            <strong>${p.title}</strong>
            <button onclick="deleteProject(${p.id})">Delete</button>
        </div>
    `
    )
    .join("");
}

async function deleteProject(id) {
  if (!confirm("Delete this project?")) return;

  await fetch(`/admin/project/${id}`, {
    method: "DELETE",
  });

  showToast("Project deleted");
  loadAdminProjects();
}

/* =========================
   CONTACT MESSAGES
========================= */
async function loadMessages() {
  const res = await fetch("/admin/messages", {
    cache: "no-store",
  });
  const messages = await res.json();

  const container = document.getElementById("adminMessages");

  if (!messages.length) {
    container.innerHTML = "<p>No messages yet.</p>";
    return;
  }

  container.innerHTML = messages
    .map(
      (m) => `
        <div class="admin-message ${m.is_read ? "read" : "unread"}">
            <div class="msg-header">
                <strong>${m.name ?? "Unknown"}</strong>
                <span>${m.email}</span>
            </div>

            <p>${m.message}</p>

            <small>${new Date(m.created_at).toLocaleString()}</small>

            <div class="msg-actions">
                <button onclick="toggleRead(${m.id})">
                    ${m.is_read ? "Mark Unread" : "Mark Read"}
                </button>
                <button onclick="replyTo('${m.email}')">Reply</button>
                <button class="danger" onclick="deleteMessage(${m.id})">
                    Delete
                </button>
            </div>
        </div>
    `
    )
    .join("");
  console.log(messages);
}

/* =========================
   MESSAGE ACTIONS
========================= */
async function toggleRead(id) {
  await fetch(`/admin/message/read/${id}`, {
    method: "POST",
  });
  loadMessages();
}

async function deleteMessage(id) {
  console.log("Deleting ID:", id);

  if (!id) {
    showToast("Invalid message ID");
    return;
  }

  if (!confirm("Delete this message?")) return;

  const res = await fetch(`/admin/message/${id}`, {
    method: "DELETE",
    credentials: "same-origin",
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.text();
    console.error("Delete error:", err);
    showToast("Delete failed");
    return;
  }

  showToast("Message deleted");
  await loadMessages();
}

function replyTo(email) {
  const reply = prompt("Enter your reply:");
  if (!reply) return;

  fetch("/admin/message/reply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, reply }),
  });

  showToast("Reply sent");
}

loadAdminProjects();
loadMessages();
/* ADD PROJECT (Admin Dashboard) */
async function addProject() {
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;
  const technologies = document.getElementById("technologies").value;

  // Basic validation before sending
  if (!title || !description) {
    showToast("Title and Description are required");
    return;
  }

  const projectData = {
    title: title,
    description: description,
    technologies: technologies, // Sent as a string
  };

  try {
    const res = await fetch("/admin/project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(projectData),
    });

    const result = await res.json();

    if (res.ok) {
      showToast("Project added successfully!");
      // Clear inputs
      document.getElementById("title").value = "";
      document.getElementById("description").value = "";
      document.getElementById("technologies").value = "";
      loadAdminProjects(); // Refresh list
    } else {
      // This will show the specific error from your Flask 'except' block
      alert("Server Error (500): " + (result.error || "Unknown error"));
    }
  } catch (err) {
    console.error("Fetch error:", err);
    showToast("Network error: Could not connect to server");
  }
}
