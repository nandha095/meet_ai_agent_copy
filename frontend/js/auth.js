async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", email);   // MUST be 'username'
  formData.append("password", password);

  const response = await fetch("http://127.0.0.1:8000/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  });

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem("token", data.access_token);
    window.location.href = "dashboard.html";
  } else {
    alert(data.detail || "Login failed");
  }
}

async function register() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const response = await fetch("http://127.0.0.1:8000/auth/register", {
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
}
