const experienceEditForm = document.getElementById("experience-edit-form");

experienceEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = experienceEditForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  const formData = new FormData(experienceEditForm);
  const payload = Object.fromEntries(
    ["title", "description", "category", "thumbnail", "ended_at"].map(
      (name) => [name, formData.get(name)]
    )
  );
  if (!payload.ended_at) payload.ended_at = null;

  try {
    const response = await fetch(experienceEditForm.dataset.apiUrl, {
      method: "PATCH",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errors = Object.values(result)
        .flat()
        .filter((value) => typeof value === "string")
        .map(String);
      throw new Error(errors.join(" ") || `Request failed (HTTP ${response.status}).`);
    }

    showToast("Success", "Experience updated successfully.", "success");
    window.setTimeout(() => {
      window.location.assign(experienceEditForm.dataset.listUrl);
    }, 500);
  } catch (error) {
    showToast("Failed to update experience", error.message, "error");
    submitButton.disabled = false;
  }
});