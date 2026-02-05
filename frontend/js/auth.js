// Automatically detects current domain (ngrok / EC2 / localhost / future domain)
const BASE_URL = window.location.origin;


// ✅ LOGIN FUNCTION
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", email);   // FastAPI OAuth expects 'username'
  formData.append("password", password);

  try {
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
      alert(data.detail || "Login failed");
    }

  } catch (error) {
    console.error("Login error:", error);
    alert("Server unreachable. Please try again.");
  }
}



// ✅ REGISTER FUNCTION
async function register() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
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
      alert("Registration successful. Please login.");
      window.location.href = "index.html";
    } else {
      alert(data.detail || "Registration failed");
    }

  } catch (error) {
    console.error("Register error:", error);
    alert("Server unreachable. Please try again.");
  }
}
