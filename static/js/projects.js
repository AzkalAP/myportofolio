const projectConfig = document.getElementById("project-config").dataset;
const loadingState = document.getElementById("loading");
const errorState = document.getElementById("error");
const emptyState = document.getElementById("empty");
const gridContainer = document.getElementById("grid");
const searchForm = document.getElementById("project-search-form");
const searchInput = document.getElementById("search-input");
const projectForm = document.getElementById("project-form");
const csrfToken = document.querySelector(
  '#csrf-token-form input[name="csrfmiddlewaretoken"]'
).value;
const isOwner = projectConfig.isOwner === "true";
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

function buildProjectCardElement(item) {
  const project = item.fields;
  const projectId = String(item.pk);
  const articleElement = document.createElement("article");
  articleElement.className = "experience-card";

  const imageHtml = project.image_path
    ? `<img src="/static/${escapeHtml(project.image_path)}" alt="Image of ${escapeHtml(project.title)}" class="project-image">`
    : "";
  const externalUrl = getSafeExternalUrl(project.external_url);
  const urlHtml = externalUrl
    ? `<a href="${escapeHtml(externalUrl)}" class="button" target="_blank" rel="noopener noreferrer">View Project</a>`
    : "";
  const starUrl = getProjectUrl(projectConfig.starUrlTemplate, projectId);
  const updateUrl = getProjectUrl(projectConfig.updateUrlTemplate, projectId);
  const deleteUrl = getProjectUrl(projectConfig.deleteUrlTemplate, projectId);
  const isStarredClass = project.is_starred ? " is-starred" : "";
  const starText = project.is_starred ? "Unstar" : "Star";
  const starCount = Number(project.star_count) || 0;
  const starTitle = starCount > 0
    ? `Starred by ${starCount} users`
    : "Be the first to star";
  const statusLabel = project.status === "finished" ? "Finished" : "In progress";
  const editHtml = canEdit
    ? `<a href="${escapeHtml(updateUrl)}" class="button">Edit Project</a>`
    : "";
  const deleteHtml = isOwner
    ? `<form method="post" action="${escapeHtml(deleteUrl)}" style="display:inline;" onsubmit="return confirm('Are you sure you want to delete this project?');"><input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken)}"><button type="submit" class="button button-danger">Delete Project</button></form>`
    : "";

  articleElement.innerHTML = `
    ${imageHtml}
    <h2>${escapeHtml(project.title)}</h2>
    <span class="experience-category">${escapeHtml(statusLabel)}</span>
    <p class="experience-description">${escapeHtml(project.description)}</p>
    <div class="project-card-actions">
      <div class="project-actions">
        ${urlHtml}
        <form method="post" action="${escapeHtml(starUrl)}" class="star-form">
          <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken)}">
          <button type="submit" class="button button-star${isStarredClass}" title="${escapeHtml(starTitle)}" aria-label="${project.is_starred ? "Remove your star" : "Star this project"}">
            <span aria-hidden="true">★</span>
            ${starText}
            <span class="star-count">${starCount}</span>
          </button>
        </form>
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
    if (!response.ok) throw new Error("Failed to fetch project data");

    const projectData = await response.json();
    if (projectData.length === 0) {
      displayPageSection({ showEmpty: true });
      return;
    }

    gridContainer.replaceChildren(
      ...projectData.map(buildProjectCardElement)
    );
    displayPageSection({ showGrid: true });
  } catch (error) {
    if (error.name === "AbortError") return;
    console.error("Error loading projects:", error);
    displayPageSection({ showError: true });
  }
}

function searchProjects() {
  fetchProjects(searchInput.value.trim());
}

searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(searchProjects, searchDebounceDelay);
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  clearTimeout(searchDebounceTimer);
  searchProjects();
});

function closeProjectModal() {
  document.getElementById("add-project-modal").hidePopover();
}

async function addProject(event) {
  event.preventDefault();
  const submitButton = projectForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  try {
    const response = await fetch(projectConfig.createEndpoint, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: new FormData(projectForm),
    });
    const result = await response.json().catch(() => ({}));

    if (response.ok) {
      projectForm.reset();
      closeProjectModal();
      showToast("Success", "New project added successfully!", "success");
      fetchProjects(searchInput.value.trim());
      return;
    }

    const errorMessages = result.errors
      ? Object.values(result.errors).flat().map((error) => error.message)
      : [result.message || `Something went wrong (status ${response.status}).`];
    showToast("Failed to add project", errorMessages.join(" "), "error");
  } catch (error) {
    console.error("Error adding project:", error);
    showToast(
      "Failed to add project",
      "Could not reach the server. Please try again.",
      "error"
    );
  } finally {
    submitButton.disabled = false;
  }
}

if (projectForm) projectForm.addEventListener("submit", addProject);

fetchProjects(searchInput.value.trim());