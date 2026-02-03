// Example JS to toggle password visibility
document.addEventListener('DOMContentLoaded', () => {
    const togglePassword = document.querySelector("#togglePassword");
    const password = document.querySelector("#password");

    if (togglePassword && password) {
        togglePassword.addEventListener("click", () => {
            const type = password.getAttribute("type") === "password" ? "text" : "password";
            password.setAttribute("type", type);
            togglePassword.classList.toggle("fa-eye-slash");
        });
    }
});
