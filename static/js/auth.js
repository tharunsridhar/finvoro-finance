if (Auth.isLoggedIn()) {
  window.location.href = "/dashboard/";
}

function showError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.style.display = "block";
}

function setLoading(isLoading) {
  const btn = document.getElementById("submit-btn");
  btn.disabled = isLoading;
  btn.textContent = isLoading ? "Please wait..." : btn.dataset.label;
}

const loginForm = document.getElementById("login-form");
if (loginForm) {
  document.getElementById("submit-btn").dataset.label = "Log in";
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: document.getElementById("email").value,
          password: document.getElementById("password").value,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(formatErrors(data));
      }
      Auth.setTokens({ access: data.access, refresh: data.refresh });
      window.location.href = "/dashboard/";
    } catch (err) {
      showError(err.message === "Failed to fetch" ? "Cannot reach the server." : err.message);
    } finally {
      setLoading(false);
    }
  });
}

const registerForm = document.getElementById("register-form");
if (registerForm) {
  document.getElementById("submit-btn").dataset.label = "Register";
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: document.getElementById("email").value,
          first_name: document.getElementById("first_name").value,
          last_name: document.getElementById("last_name").value,
          password: document.getElementById("password").value,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(formatErrors(data));
      }
      window.location.href = "/login/";
    } catch (err) {
      showError(err.message === "Failed to fetch" ? "Cannot reach the server." : err.message);
    } finally {
      setLoading(false);
    }
  });
}
