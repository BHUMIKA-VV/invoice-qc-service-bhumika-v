const API_URL = import.meta.env.VITE_API_URL;
console.log("Loaded API URL =", API_URL);

export async function validateJSON(payload: any) {
  const response = await fetch(`${API_URL}/validate-json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText);
  }

  return await response.json();
}

export async function validatePDFs(files: File[]) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await fetch(`${API_URL}/extract-and-validate-pdfs`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText);
  }

  return await response.json();
}
