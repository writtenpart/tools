document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const loading = document.getElementById("loading");
  const output = document.getElementById("output");
  const downloadBtn = document.getElementById("downloadBtn");

  loading.classList.remove("hidden");
  downloadBtn.classList.add("hidden");
  output.value = "";

  const fileInput = document.getElementById("fileInput");
  const engineSelect = document.getElementById("engineSelect");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("engine", engineSelect.value);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (data.error) {
      output.value = "❌ Error: " + data.error;
    } else {
      output.value = data.text;
      downloadBtn.classList.remove("hidden");
    }
  } catch (err) {
    output.value = "⚠️ Upload failed: " + err;
  } finally {
    loading.classList.add("hidden");
  }
});

// Download button handler
document.getElementById("downloadBtn").addEventListener("click", () => {
  window.location.href = "/download";
});
