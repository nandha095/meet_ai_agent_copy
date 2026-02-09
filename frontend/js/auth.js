// Automatically detects current domain (ngrok / EC2 / localhost / future domain)
const BASE_URL = window.location.origin;


// ✅ LOGIN FUNCTION
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password")?.value;
  const messageEl = document.getElementById("auth-message");
  const btn = document.getElementById("login-btn");
  const emailEl = document.getElementById("email");
  const passwordEl = document.getElementById("password");
  const confirmPasswordEl = document.getElementById("confirm_password");
  const emailErrorEl = document.getElementById("email-error");
  const passwordErrorEl = document.getElementById("password-error");
  const confirmPasswordErrorEl = document.getElementById("confirm-password-error");
  const passwordHintEl = document.getElementById("password-hint");
  const rememberEl = document.getElementById("remember");

  if (messageEl) {
    messageEl.className = "message";
    messageEl.textContent = "";
  }
  if (emailErrorEl) emailErrorEl.textContent = "";
  if (passwordErrorEl) passwordErrorEl.textContent = "";
  if (confirmPasswordErrorEl) confirmPasswordErrorEl.textContent = "";
  if (passwordHintEl) passwordHintEl.textContent = "";

  if (emailEl) emailEl.classList.remove("input-error");
  if (passwordEl) passwordEl.classList.remove("input-error");
  if (confirmPasswordEl) confirmPasswordEl.classList.remove("input-error");

  if (!email || !email.includes("@")) {
    if (emailEl) emailEl.classList.add("input-error");
    if (emailErrorEl) emailErrorEl.textContent = "Enter a valid email.";
    if (messageEl) {
      messageEl.className = "message error";
      messageEl.textContent = "";
    }
    return;
  }

  if (!password) {
    if (passwordEl) passwordEl.classList.add("input-error");
    if (passwordErrorEl) passwordErrorEl.textContent = "Please enter your password.";
    return;
  }

  const formData = new URLSearchParams();
  formData.append("username", email);   // FastAPI OAuth expects 'username'
  formData.append("password", password);
  formData.append("remember", rememberEl && rememberEl.checked ? "true" : "false");

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Signing in...";
    }

    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.access_token);

      // Redirect after login
      window.location.href = "dashboard.html";
    } else {
      const msg = data.detail || "Login failed";
      const lowerMsg = msg.toLowerCase();
      if (lowerMsg.includes("email")) {
        if (emailEl) emailEl.classList.add("input-error");
        if (emailErrorEl) emailErrorEl.textContent = msg;
      } else if (lowerMsg.includes("invalid email or password")) {
        if (passwordEl) passwordEl.classList.add("input-error");
        if (passwordErrorEl) passwordErrorEl.textContent = "Please enter the correct password or reset your password.";
        if (passwordHintEl) {
          passwordHintEl.innerHTML = `Forgot it? <a href="forgot-password.html">Reset your password</a>`;
        }
      } else if (lowerMsg.includes("password")) {
        if (passwordEl) passwordEl.classList.add("input-error");
        if (passwordErrorEl) passwordErrorEl.textContent = msg;
      } else if (messageEl) {
        messageEl.className = "message error";
        messageEl.textContent = msg;
      }
    }

  } catch (error) {
    console.error("Login error:", error);
    if (messageEl) {
      messageEl.className = "message error";
      messageEl.textContent = "Server unreachable. Please try again.";
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Sign in";
    }
  }
}



// ✅ REGISTER FUNCTION
async function register() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const messageEl = document.getElementById("auth-message");
  const btn = document.getElementById("register-btn");
  const emailEl = document.getElementById("email");
  const passwordEl = document.getElementById("password");
  const emailErrorEl = document.getElementById("email-error");
  const passwordErrorEl = document.getElementById("password-error");

  if (messageEl) {
    messageEl.className = "message";
    messageEl.textContent = "";
  }
  if (emailErrorEl) emailErrorEl.textContent = "";
  if (passwordErrorEl) passwordErrorEl.textContent = "";

  if (emailEl) emailEl.classList.remove("input-error");
  if (passwordEl) passwordEl.classList.remove("input-error");

  if (!email || !email.includes("@")) {
    if (emailEl) emailEl.classList.add("input-error");
    if (emailErrorEl) emailErrorEl.textContent = "Enter a valid email.";
    if (messageEl) {
      messageEl.className = "message error";
      messageEl.textContent = "";
    }
    return;
  }

  if (!password) {
    if (passwordEl) passwordEl.classList.add("input-error");
    if (passwordErrorEl) passwordErrorEl.textContent = "Please enter your password.";
    return;
  }

  if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password) || !/[^\w\s]/.test(password)) {
    if (passwordEl) passwordEl.classList.add("input-error");
    if (passwordErrorEl) passwordErrorEl.textContent = "8+ chars, upper, lower, number, symbol.";
    if (messageEl) {
      messageEl.className = "message error";
      messageEl.textContent = "";
    }
    return;
  }

  if (confirmPasswordEl && password !== confirmPassword) {
    confirmPasswordEl.classList.add("input-error");
    if (confirmPasswordErrorEl) confirmPasswordErrorEl.textContent = "Passwords do not match.";
    return;
  }

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Creating...";
    }

    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (response.ok) {
      if (messageEl) {
        messageEl.className = "message success";
        messageEl.textContent = "Registration successful. Redirecting to sign in...";
      }
      setTimeout(() => {
        window.location.href = "login.html";
      }, 1200);
    } else {
      const msg = data.detail || "Registration failed";
      if (msg.toLowerCase().includes("email")) {
        if (emailEl) emailEl.classList.add("input-error");
        if (emailErrorEl) emailErrorEl.textContent = msg;
      } else if (msg.toLowerCase().includes("password")) {
        if (passwordEl) passwordEl.classList.add("input-error");
        if (passwordErrorEl) passwordErrorEl.textContent = msg;
      } else if (messageEl) {
        messageEl.className = "message error";
        messageEl.textContent = msg;
      }
    }

  } catch (error) {
    console.error("Register error:", error);
    if (messageEl) {
      messageEl.className = "message error";
      messageEl.textContent = "Server unreachable. Please try again.";
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Create account";
    }
  }
}
