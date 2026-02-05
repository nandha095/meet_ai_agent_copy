// ✅ Automatically detect server URL
const BASE_URL = window.location.origin;


/****************************
 * SEND RESET LINK
 ****************************/
async function sendResetLink() {
  const email = document.getElementById("email").value;
  const messageEl = document.getElementById("message");

  if (!email) {
    messageEl.innerText = "❌ Please enter your email";
    return;
  }

  messageEl.innerText = "🤖 AI is sending reset link...";

  try {
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
      messageEl.innerText =
        "✅ Reset link sent. Check your email inbox.";
    } else {
      messageEl.innerText = data.detail || "❌ Failed to send reset link";
    }

  } catch (err) {
    console.error("Forgot password error:", err);
    messageEl.innerText = "❌ Server unreachable. Try again.";
  }
}


/****************************
 * RESET PASSWORD
 ****************************/
async function resetPassword() {
  const password = document.getElementById("password").value;
  const messageEl = document.getElementById("message");

  // Get token from URL
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token || !password) {
    messageEl.innerText = "❌ Invalid reset request";
    return;
  }

  messageEl.innerText = "🤖 AI is resetting your password...";

  try {
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
      messageEl.innerText =
        "✅ Password reset successful. Redirecting to login...";

      setTimeout(() => {
        window.location.href = "index.html";
      }, 2000);

    } else {
      messageEl.innerText = data.detail || "❌ Reset failed";
    }

  } catch (err) {
    console.error("Reset password error:", err);
    messageEl.innerText = "❌ Server unreachable. Try again.";
  }
}
