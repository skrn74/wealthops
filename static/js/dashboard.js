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