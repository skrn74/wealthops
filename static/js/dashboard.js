console.log("dashboard.js loaded");

async function updateDashboard() {

    try {

        const response = await fetch("/api/dashboard");

        const data = await response.json();

        document.getElementById("totalValue").innerHTML =
            "₹" + Number(data.total_value).toLocaleString();

        document.getElementById("investmentValue").innerHTML =
            "₹" + Number(data.investment).toLocaleString();

        document.getElementById("gainValue").innerHTML =
            "₹" + Number(data.gain).toLocaleString();

    }
    catch(error){
        console.error(error);
    }

}

// Load immediately
updateDashboard();

// Refresh every 5 seconds
setInterval(updateDashboard, 5000);

// Portfolio Privacy Mode
document.addEventListener("DOMContentLoaded", function () {

    const toggle = document.getElementById("privacyToggle");

    if (!toggle) return;

    const values = document.querySelectorAll(".financial-value");

    let hidden = localStorage.getItem("wealthopsPrivacy") === "true";

    function updatePrivacyMode() {

        values.forEach(value => {
            value.style.filter = hidden ? "blur(8px)" : "none";
        });

        toggle.textContent = hidden ? "🙈" : "👁️";

        toggle.title = hidden
            ? "Show portfolio values"
            : "Hide portfolio values";
    }

    toggle.addEventListener("click", function () {

        hidden = !hidden;

        localStorage.setItem(
            "wealthopsPrivacy",
            hidden
        );

        updatePrivacyMode();
    });

    updatePrivacyMode();
});