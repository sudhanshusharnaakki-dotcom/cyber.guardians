// ========================================
// CYBER GUARDIANS - FISHSHIELD AI
// JAVASCRIPT
// ========================================


// Scroll to Detector Section
function scrollToDetector() {

    document
        .getElementById("detector")
        .scrollIntoView({
            behavior: "smooth"
        });

}


// Analyze User Input
async function analyzeInput() {

    const input =
        document
            .getElementById("userInput")
            .value
            .trim();


    // Empty input check
    if (!input) {

        alert(
            "⚠️ Please enter a message or URL to analyze!"
        );

        return;

    }


    const resultBox =
        document.getElementById("result");


    const riskTitle =
        document.getElementById("riskTitle");


    const riskScore =
        document.getElementById("riskScore");


    const reasonsBox =
        document.getElementById("reasons");


    const recommendationBox =
        document.getElementById("recommendation");


    const riskFill =
        document.getElementById("riskFill");


    // Loading State
    resultBox.style.display = "block";

    riskTitle.innerHTML =
        "🔍 FishShield AI is analyzing...";

    riskScore.innerHTML = "";

    reasonsBox.innerHTML = "";

    recommendationBox.innerHTML = "";

    riskFill.style.width = "0%";


    try {

        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            text: input
                        })
                }
            );


        const data =
            await response.json();


        // Risk Title
        riskTitle.innerHTML =
            data.risk;


        // Risk Score
        riskScore.innerHTML =
            "Risk Score: " +
            data.score +
            "%";


        // Risk Bar
        riskFill.style.width =
            data.score + "%";


        // Reasons
        let reasonsHTML =
            "<h3>🔎 What is suspicious and why?</h3>";


        if (
            data.reasons &&
            data.reasons.length > 0
        ) {

            reasonsHTML += "<ul>";


            data.reasons.forEach(
                function (reason) {

                    reasonsHTML +=
                        "<li>" +
                        reason +
                        "</li>";

                }
            );


            reasonsHTML += "</ul>";

        }

        else {

            reasonsHTML +=
                "<p>No major suspicious indicators detected.</p>";

        }


        reasonsBox.innerHTML =
            reasonsHTML;


        // Recommendation
        recommendationBox.innerHTML =
            `
            <h3>🛡️ Safety Recommendation</h3>

            <p>
                ${data.recommendation}
            </p>
            `;


        // Scroll to Result
        resultBox.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });


    }

    catch (error) {

        console.error(
            "FishShield Error:",
            error
        );


        riskTitle.innerHTML =
            "❌ Analysis Failed";


        reasonsBox.innerHTML =
            `
            <p>
                Unable to connect to
                FishShield AI server.
                Please try again.
            </p>
            `;

    }

}
