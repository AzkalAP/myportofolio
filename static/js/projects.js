const projectConfig = document.getElementById("project-config").dataset;
const loadingState = document.getElementById("loading");
const errorState = document.getElementById("error");
const emptyState = document.getElementById("empty");
const gridContainer = document.getElementById("grid");
const searchForm = document.getElementById("project-search-form");
const searchInput = document.getElementById("search-input");
const projectForm = document.getElementById("project-form");
const isOwner = projectConfig.isOwner === "true";
const isAuthenticated = projectConfig.isAuthenticated === "true";
const canEdit = isOwner || projectConfig.isEditor === "true";
const searchDebounceDelay = 300;
let searchDebounceTimer;
let projectsAbortController;

function displayPageSection({
  showLoading = false,
  showError = false,
  showEmpty = false,
  showGrid = false,
}) {
  loadingState.classList.toggle("hide", !showLoading);
  errorState.classList.toggle("hide", !showError);
  emptyState.classList.toggle("hide", !showEmpty);
  gridContainer.classList.toggle("hide", !showGrid);
}

function getCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getProjectUrl(template, projectId) {
  return template.replace("/0/", `/${encodeURIComponent(projectId)}/`);
}

function getSafeExternalUrl(value) {
  try {
    const url = new URL(value, window.location.origin);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

function buildProjectCardElement(project) {
  const articleElement = document.createElement("article");
  articleElement.className = "experience-card";

  const imageHtml = project.image_path
    ? `<img src="/static/${escapeHtml(project.image_path)}" alt="Image of ${escapeHtml(project.title)}" class="project-image">`
    : "";
  const externalUrl = getSafeExternalUrl(project.external_url);
  const urlHtml = externalUrl
    ? `<a href="${escapeHtml(externalUrl)}" class="button" target="_blank" rel="noopener noreferrer">View Project</a>`
    : "";
  const starUrl = getProjectUrl(
    projectConfig.starUrlTemplate,
    project.id,
  );
  const detailUrl = getProjectUrl(
    projectConfig.detailUrlTemplate,
    project.id,
  );
  const updateUrl = getProjectUrl(
    projectConfig.updateUrlTemplate,
    project.id,
  );
  const starCount = Number(project.star_count) || 0;
  const statusLabel = project.status === "finished" ? "Finished" : "In progress";
  const starHtml = isAuthenticated
    ? `<button type="button" class="button button-star${project.is_starred ? " is-starred" : ""}" data-action="star" data-id="${escapeHtml(project.id)}" title="${escapeHtml(project.starred_by_names)}" aria-label="${project.is_starred ? "Remove your star" : "Star this project"}"><span aria-hidden="true">★</span>${project.is_starred ? "Unstar" : "Star"}<span class="star-count">${starCount}</span></button>`
    : `<a href="${escapeHtml(projectConfig.loginUrl)}" class="button">Login to star <span class="star-count">${starCount}</span></a>`;
  const editHtml = canEdit
    ? `<a href="${escapeHtml(updateUrl)}" class="button">Edit Project</a>`
    : "";
  const deleteHtml = isOwner
    ? `<button type="button" class="button button-danger" data-action="delete" data-id="${escapeHtml(project.id)}">Delete Project</button>`
    : "";

  articleElement.innerHTML = `
    ${imageHtml}
    <h2>${escapeHtml(project.title)}</h2>
    <span class="experience-category">${escapeHtml(statusLabel)}</span>
    <p class="experience-description">${escapeHtml(project.description)}</p>
    <div class="project-card-actions">
      <div class="project-actions">
        ${urlHtml}
        ${starHtml}
        ${editHtml}
        ${deleteHtml}
      </div>
    </div>
  `;
  return articleElement;
}

async function fetchProjects(searchQuery = "") {
  if (projectsAbortController) projectsAbortController.abort();
  projectsAbortController = new AbortController();

  try {
    displayPageSection({ showLoading: true });
    const url = new URL(projectConfig.projectsEndpoint, window.location.origin);
    if (searchQuery) url.searchParams.set("title", searchQuery);

    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      signal: projectsAbortController.signal,
    });
    if (!response.ok) throw new Error(`Request failed (HTTP ${response.status}).`);

    const projects = await response.json();
    gridContainer.replaceChildren(...projects.map(buildProjectCardElement));
    displayPageSection({
      showGrid: projects.length > 0,
      showEmpty: projects.length === 0,
    });
  } catch (error) {
    if (error.name === "AbortError") return;
    console.error("Error loading projects:", error);
    displayPageSection({ showError: true });
  }
}

function apiErrorMessage(data, status) {
  const messages = Object.values(data)
    .flat()
    .filter((value) => typeof value === "string");
  return messages.join(" ") || `Request failed (HTTP ${status}).`;
}

async function writeProject(url, method, payload) {
  const headers = {
    Accept: "application/json",
    "X-CSRFToken": getCookie("csrftoken"),
  };
  const options = { method, headers };
  if (payload !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }

  const response = await fetch(url, options);
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
  return data;
}

async function addProject(event) {
  event.preventDefault();
  const button = projectForm.querySelector('button[type="submit"]');
  button.disabled = true;

  try {
    const formData = new FormData(projectForm);
    const payload = Object.fromEntries(
      ["title", "description", "status", "image_path", "external_url"]
        .map((name) => [name, formData.get(name)]),
    );
    await writeProject(projectConfig.projectsEndpoint, "POST", payload);
    projectForm.reset();
    document.getElementById("add-project-modal").hidePopover();
    showToast("Success", "New project added successfully!", "success");
    await fetchProjects(searchInput.value.trim());
  } catch (error) {
    showToast("Failed to add project", error.message, "error");
  } finally {
    button.disabled = false;
  }
}

if (projectForm) projectForm.addEventListener("submit", addProject);

gridContainer.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled) return;

  const action = button.dataset.action;
  if (action === "delete" && !window.confirm("Are you sure you want to delete this project?")) {
    return;
  }

  button.disabled = true;
  const url = action === "star"
    ? getProjectUrl(projectConfig.starUrlTemplate, button.dataset.id)
    : getProjectUrl(projectConfig.detailUrlTemplate, button.dataset.id);
  const method = action === "star" ? "POST" : "DELETE";

  try {
    await writeProject(url, method);
    showToast(
      "Success",
      action === "star" ? "Star updated." : "Project deleted.",
      "success",
    );
    await fetchProjects(searchInput.value.trim());
  } catch (error) {
    showToast("Request failed", error.message, "error");
  } finally {
    button.disabled = false;
  }
});

searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(
    () => fetchProjects(searchInput.value.trim()),
    searchDebounceDelay,
  );
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  clearTimeout(searchDebounceTimer);
  fetchProjects(searchInput.value.trim());
});

fetchProjects(searchInput.value.trim());