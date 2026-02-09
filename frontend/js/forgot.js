// ✅ Automatically detect server URL
const BASE_URL = window.location.origin;


/****************************
 * SEND RESET LINK
 ****************************/
async function sendResetLink() {
  const email = document.getElementById("email").value;
  const messageEl = document.getElementById("message");
  const btn = document.getElementById("reset-link-btn");
  const emailEl = document.getElementById("email");
  const emailErrorEl = document.getElementById("email-error");

  if (!email) {
    if (emailEl) emailEl.classList.add("input-error");
    if (emailErrorEl) emailErrorEl.textContent = "Email is required.";
    messageEl.className = "message error";
    messageEl.innerText = "";
    return;
  }

  if (emailEl) emailEl.classList.remove("input-error");
  if (emailErrorEl) emailErrorEl.textContent = "";
  if (!email.includes("@")) {
    if (emailEl) emailEl.classList.add("input-error");
    if (emailErrorEl) emailErrorEl.textContent = "Enter a valid email.";
    messageEl.className = "message error";
    messageEl.innerText = "";
    return;
  }

  messageEl.className = "message";
  messageEl.innerText = "🤖 AI is sending reset link...";

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sending...";
    }

    const response = await fetch(
      `${BASE_URL}/auth/forgot-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email })
      }
    );

    const data = await response.json();

    if (response.ok) {
      messageEl.className = "message success";
      messageEl.innerText = "✅ Reset link sent. Check your email inbox.";
    } else {
      messageEl.className = "message error";
      if (data.detail && data.detail.toLowerCase().includes("email")) {
        if (emailEl) emailEl.classList.add("input-error");
        if (emailErrorEl) emailErrorEl.textContent = data.detail;
        messageEl.innerText = "";
      } else {
        messageEl.innerText = data.detail || "❌ Failed to send reset link";
      }
    }

  } catch (err) {
    console.error("Forgot password error:", err);
    messageEl.className = "message error";
    messageEl.innerText = "❌ Server unreachable. Try again.";
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Send reset link";
    }
  }
}


/****************************
 * RESET PASSWORD
 ****************************/
async function resetPassword() {
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password")?.value;
  const messageEl = document.getElementById("message");
  const btn = document.getElementById("reset-btn");
  const passwordEl = document.getElementById("password");
  const passwordErrorEl = document.getElementById("password-error");
  const confirmPasswordEl = document.getElementById("confirm_password");
  const confirmPasswordErrorEl = document.getElementById("confirm-password-error");

  // Get token from URL
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token || !password) {
    if (passwordEl) passwordEl.classList.add("input-error");
    if (passwordErrorEl) passwordErrorEl.textContent = "Please enter your password.";
    messageEl.className = "message error";
    messageEl.innerText = "";
    return;
  }

  if (passwordEl) passwordEl.classList.remove("input-error");
  if (passwordErrorEl) passwordErrorEl.textContent = "";
  if (confirmPasswordEl) confirmPasswordEl.classList.remove("input-error");
  if (confirmPasswordErrorEl) confirmPasswordErrorEl.textContent = "";
  if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password) || !/[^\w\s]/.test(password)) {
    if (passwordEl) passwordEl.classList.add("input-error");
    if (passwordErrorEl) passwordErrorEl.textContent = "8+ chars, upper, lower, number, symbol.";
    messageEl.className = "message error";
    messageEl.innerText = "";
    return;
  }

  if (confirmPasswordEl && password !== confirmPassword) {
    confirmPasswordEl.classList.add("input-error");
    if (confirmPasswordErrorEl) confirmPasswordErrorEl.textContent = "Passwords do not match.";
    messageEl.className = "message error";
    messageEl.innerText = "";
    return;
  }

  messageEl.className = "message";
  messageEl.innerText = "🤖 AI is resetting your password...";

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Updating...";
    }

    const response = await fetch(
      `${BASE_URL}/auth/reset-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          token,
          new_password: password
        })
      }
    );

    const data = await response.json();

    if (response.ok) {
      messageEl.className = "message success";
      messageEl.innerText = "✅ Password reset successful. Redirecting to login...";

      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);

    } else {
      messageEl.className = "message error";
      if (data.detail && data.detail.toLowerCase().includes("password")) {
        if (passwordEl) passwordEl.classList.add("input-error");
        if (passwordErrorEl) passwordErrorEl.textContent = data.detail;
        messageEl.innerText = "";
      } else {
        messageEl.innerText = data.detail || "❌ Reset failed";
      }
    }

  } catch (err) {
    console.error("Reset password error:", err);
    messageEl.className = "message error";
    messageEl.innerText = "❌ Server unreachable. Try again.";
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Update password";
    }
  }
}
