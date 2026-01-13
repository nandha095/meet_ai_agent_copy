function connectGoogle() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "index.html";
    return;
  }

  window.location.href = "http://127.0.0.1:8000/auth/google/login";
}


async function sendProposal() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    return;
  }

  const payload = {
    to_email: document.getElementById("to_email").value,
    subject: document.getElementById("subject").value,
    body: document.getElementById("body").value
  };

  const response = await fetch(
    "http://127.0.0.1:8000/emails/send-proposal",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    }
  );

  const data = await response.json();

  if (response.ok) {
    alert("Proposal sent successfully");
  } else {
    alert(data.detail);
  }
}
