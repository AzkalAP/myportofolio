const experienceConfig = document.getElementById("experience-config").dataset;
const experienceSearchForm = document.getElementById("experience-search-form");
const experienceSearchInput = document.getElementById("experience-search-input");
const experienceCreateForm = document.getElementById("experience-create-form");
const experienceAddModal = document.getElementById("add-experience-modal");
const experienceLoading = document.getElementById("experience-loading");
const experienceError = document.getElementById("experience-error");
const experienceEmpty = document.getElementById("experience-empty");
const experienceEmptyMessage = document.getElementById("experience-empty-message");
const experienceGrid = document.getElementById("experience-grid");
const experienceCsrfToken = document.querySelector(
  '#experience-csrf-form input[name="csrfmiddlewaretoken"]'
).value;
const isExperienceOwner = experienceConfig.isOwner === "true";
const canEditExperience = isExperienceOwner || experienceConfig.isEditor === "true";
const isExperienceAuthenticated = experienceConfig.isAuthenticated === "true";
const searchDebounceDelay = 300;
const experienceIdPlaceholder = "00000000-0000-0000-0000-000000000000";
let searchDebounceTimer;
let experienceAbortController;

function showExperienceState(state) {
  experienceLoading.classList.toggle("hide", state !== "loading");
  experienceError.classList.toggle("hide", state !== "error");
  experienceEmpty.classList.toggle("hide", state !== "empty");
  experienceGrid.classList.toggle("hide", state !== "results");
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function getExperienceUrl(template, experienceId) {
  return template.replace(
    experienceIdPlaceholder,
    encodeURIComponent(String(experienceId))
  );
}

function getSafeImageUrl(value) {
  if (!value) return "";

  try {
    const imageUrl = new URL(value, window.location.origin);
    return ["http:", "https:"].includes(imageUrl.protocol) ? imageUrl.href : "";
  } catch {
    return "";
  }
}

function createDeleteConfirmation(experience, deleteUrl) {
  const experienceId = String(experience.pk).replace(/[^a-zA-Z0-9_-]/g, "");
  const popoverId = `delete-experience-${experienceId}`;
  const dialogTitleId = `${popoverId}-title`;
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "button button-danger";
  trigger.setAttribute("popovertarget", popoverId);
  trigger.setAttribute("aria-label", `Delete ${experience.fields.title}`);
  trigger.textContent = "Delete Experience";

  const popover = document.createElement("div");
  popover.id = popoverId;
  popover.className = "project-delete-modal";
  popover.setAttribute("popover", "auto");
  popover.setAttribute("role", "dialog");
  popover.setAttribute("aria-modal", "true");
  popover.setAttribute("aria-labelledby", dialogTitleId);

  const backdrop = document.createElement("button");
  backdrop.type = "button";
  backdrop.className = "project-delete-modal__backdrop";
  backdrop.setAttribute("popovertarget", popoverId);
  backdrop.setAttribute("popovertargetaction", "hide");
  backdrop.setAttribute("aria-label", "Close delete confirmation");

  const content = document.createElement("div");
  content.className = "project-delete-modal__content";

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "project-delete-modal__close";
  closeButton.setAttribute("popovertarget", popoverId);
  closeButton.setAttribute("popovertargetaction", "hide");
  closeButton.setAttribute("aria-label", "Close delete confirmation");
  closeButton.textContent = "×";

  const title = createTextElement("h2", "", "Delete Experience?");
  title.id = dialogTitleId;

  const message = document.createElement("p");
  message.append(document.createTextNode("Are you sure you want to delete "));
  const experienceTitle = createTextElement(
    "strong",
    "",
    experience.fields.title
  );
  message.append(experienceTitle, document.createTextNode("?"));

  const actions = document.createElement("div");
  actions.className = "project-delete-modal__actions";

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "button button-secondary";
  cancelButton.setAttribute("popovertarget", popoverId);
  cancelButton.setAttribute("popovertargetaction", "hide");
  cancelButton.textContent = "Cancel";

  const deleteForm = document.createElement("form");
  deleteForm.method = "post";
  deleteForm.action = deleteUrl;

  const csrfInput = document.createElement("input");
  csrfInput.type = "hidden";
  csrfInput.name = "csrfmiddlewaretoken";
  csrfInput.value = experienceCsrfToken;

  const confirmButton = document.createElement("button");
  confirmButton.type = "submit";
  confirmButton.className = "button button-danger";
  confirmButton.textContent = "Yes, Delete";

  deleteForm.append(csrfInput, confirmButton);
  actions.append(cancelButton, deleteForm);
  content.append(closeButton, title, message, actions);
  popover.append(backdrop, content);

  return { trigger, popover };
}

function buildExperienceCard(item) {
  const experience = item.fields;
  const article = document.createElement("article");
  article.className = "experience-card";

  const imageUrl = getSafeImageUrl(experience.thumbnail);
  if (imageUrl) {
    const image = document.createElement("img");
    image.className = "project-image";
    image.src = imageUrl;
    image.alt = `Image of ${experience.title}`;
    article.append(image);
  }

  article.append(
    createTextElement("span", "experience-category", experience.category_display),
    createTextElement("h2", "", experience.title),
    createTextElement("p", "experience-description", experience.description),
    createTextElement(
      "p",
      "experience-status",
      experience.is_ongoing ? "Ongoing" : "Completed"
    )
  );

  const actions = document.createElement("div");
  actions.className = "project-actions";

  if (isExperienceAuthenticated) {
    const starButton = document.createElement("button");
    starButton.type = "button";
    starButton.className = `button button-star${
      experience.is_starred ? " is-starred" : ""
    }`;
    starButton.dataset.starUrl = getExperienceUrl(
      experienceConfig.starUrlTemplate,
      item.pk
    );
    starButton.setAttribute("aria-pressed", String(experience.is_starred));
    starButton.setAttribute(
      "aria-label",
      experience.is_starred ? "Remove your star" : "Star this experience"
    );
    starButton.title = `${experience.star_count} stars`;

    const starIcon = createTextElement("span", "", "★");
    starIcon.setAttribute("aria-hidden", "true");
    const starCount = createTextElement(
      "span",
      "star-count",
      String(Number(experience.star_count) || 0)
    );
    starButton.append(
      starIcon,
      document.createTextNode(experience.is_starred ? " Unstar " : " Star "),
      starCount
    );
    actions.append(starButton);
  } else {
    actions.append(
      createTextElement(
        "span",
        "experience-star-count",
        `★ ${Number(experience.star_count) || 0} stars`
      )
    );
  }

  if (canEditExperience) {
    const editLink = document.createElement("a");
    editLink.className = "button";
    editLink.href = getExperienceUrl(
      experienceConfig.updateUrlTemplate,
      item.pk
    );
    editLink.textContent = "Edit Experience";
    actions.append(editLink);
  }

  article.append(actions);

  if (isExperienceOwner) {
    const deleteConfirmation = createDeleteConfirmation(
      item,
      getExperienceUrl(experienceConfig.deleteUrlTemplate, item.pk)
    );
    actions.append(deleteConfirmation.trigger);
    article.append(deleteConfirmation.popover);
  }

  return article;
}

async function fetchExperiences(searchQuery = "") {
  if (experienceAbortController) experienceAbortController.abort();
  experienceAbortController = new AbortController();
  const currentController = experienceAbortController;

  showExperienceState("loading");
  const endpoint = new URL(
    experienceConfig.experiencesEndpoint,
    window.location.origin
  );
  if (searchQuery) endpoint.searchParams.set("title", searchQuery);

  try {
    const response = await fetch(endpoint, {
      headers: { Accept: "application/json" },
      signal: currentController.signal,
    });
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const experienceData = await response.json();
    if (currentController.signal.aborted) return;

    if (experienceData.length === 0) {
      experienceEmptyMessage.textContent = searchQuery
        ? "No experience found for that title."
        : "No experience has been added yet.";
      showExperienceState("empty");
      return;
    }

    experienceGrid.replaceChildren(
      ...experienceData.map(buildExperienceCard)
    );
    showExperienceState("results");
  } catch (error) {
    if (error.name === "AbortError") return;
    showExperienceState("error");
  }
}

experienceSearchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(
    () => fetchExperiences(experienceSearchInput.value.trim()),
    searchDebounceDelay
  );
});

experienceSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  clearTimeout(searchDebounceTimer);
  fetchExperiences(experienceSearchInput.value.trim());
});

document.getElementById("experience-retry").addEventListener("click", () => {
  fetchExperiences(experienceSearchInput.value.trim());
});

experienceGrid.addEventListener("click", async (event) => {
  const starButton = event.target.closest("button[data-star-url]");
  if (!starButton) return;

  starButton.disabled = true;
  try {
    const response = await fetch(starButton.dataset.starUrl, {
      method: "POST",
      headers: { "X-CSRFToken": experienceCsrfToken },
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.message || "Could not update the star.");
    }

    showToast("Star updated", "Your experience star was saved.", "success");
    fetchExperiences(experienceSearchInput.value.trim());
  } catch (error) {
    showToast("Star update failed", error.message, "error");
    starButton.disabled = false;
  }
});

if (experienceCreateForm) {
  experienceCreateForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = experienceCreateForm.querySelector(
      'button[type="submit"]'
    );
    submitButton.disabled = true;
    const formData = new FormData(experienceCreateForm);
    const formCsrfToken = formData.get("csrfmiddlewaretoken") || experienceCsrfToken;

    try {
      const response = await fetch(experienceConfig.createEndpoint, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "X-CSRFToken": String(formCsrfToken),
        },
        body: formData,
      });
      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        const fieldErrors = result.errors
          ? Object.values(result.errors)
              .flatMap((errors) => errors)
              .map((error) => error.message || String(error))
          : [];
        const message =
          fieldErrors.join(" ") ||
          result.message ||
          `Something went wrong (status ${response.status}).`;
        showToast("Failed to add experience", message, "error");
        return;
      }

      experienceCreateForm.reset();
      experienceAddModal.hidePopover();
      showToast(
        "Success",
        result.message || "Experience added successfully.",
        "success"
      );
      fetchExperiences(experienceSearchInput.value.trim());
    } catch (error) {
      showToast(
        "Failed to add experience",
        "Could not reach the server. Please try again.",
        "error"
      );
    } finally {
      submitButton.disabled = false;
    }
  });
}

fetchExperiences();