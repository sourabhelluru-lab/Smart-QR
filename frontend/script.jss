function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    if (username === "admin" && password === "admin123") {
        window.location.href = "index.html";  // go to batch input page
    } else {
        alert("Invalid username or password.");
    }
}
