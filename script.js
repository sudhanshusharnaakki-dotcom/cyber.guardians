// ===============================
// SCROLL TO DETECTOR
// ===============================

function scrollToDetector() {

    document.getElementById("detector").scrollIntoView({
        behavior: "smooth"
    });

}


// ===============================
// PHISHING ANALYSIS
// ===============================

async function analyzeInput() {

    const input = document
        .getElementById("userInput")
        .value
        .trim();


    // Empty input check
    if (input === "") {

        alert("Please enter a message or URL first!");

        return;

    }


    // Get analyze button
    const button = document.querySelector(
        "#detector button"
    );


    // Loading state
    button.innerText = "⏳ ANALYZING...";
    button.disabled = true;


    try {

        // Send data to Python Backend
        const response = await fetch("/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: input
            })

        });


        const data = await response.json();


        // Show result
        document.getElementById("result")
            .style.display = "block";


        // Risk level
        document.getElementById("riskTitle")
            .innerHTML = data.risk;


        // Risk score
        document.getElementById("riskScore")
            .innerHTML =
            "<strong>" +
            data.score +
            "% Risk</strong>";


        // Risk bar
        const riskFill =
            document.getElementById("riskFill");


        riskFill.style.width =
            data.score + "%";


        // Risk bar color
        if (data.score >= 60) {

            riskFill.style.background = "#ff4d4d";

        }

        else if (data.score >= 30) {

            riskFill.style.background = "#ffc107";

        }

        else {

            riskFill.style.background = "#39c6ff";

        }


        // Reasons
        let reasonHTML =
            "<h3>🔍 Why is it suspicious?</h3>";


        if (data.reasons.length === 0) {

            reasonHTML +=
                "<p>🟢 No major warning indicators found.</p>";

        }

        else {

            data.reasons.forEach(function(reason) {

                reasonHTML +=
                    "<p>" + reason + "</p>";

            });

        }


        document.getElementById("reasons")
            .innerHTML = reasonHTML;


        // Recommendation
        document.getElementById("recommendation")
            .innerHTML =
            "<br><h3>🛡️ Safety Recommendation</h3>" +
            "<p>" +
            data.recommendation +
            "</p>";


        // Scroll to result
        document.getElementById("result")
            .scrollIntoView({
                behavior: "smooth"
            });


    }

    catch (error) {

        alert(
            "Unable to analyze. Please make sure the Python server is running."
        );

        console.error(error);

    }


    // Reset button
    button.innerText = "🔍 ANALYZE NOW";

    button.disabled = false;

}


// ===============================
// LIVE CYBER BACKGROUND
// ===============================

const canvas =
    document.getElementById("cyberCanvas");


if (canvas) {

    const ctx = canvas.getContext("2d");


    function resizeCanvas() {

        canvas.width = window.innerWidth;

        canvas.height = window.innerHeight;

    }


    resizeCanvas();


    const particles = [];


    // Create particles
    for (let i = 0; i < 80; i++) {

        particles.push({

            x: Math.random() * canvas.width,

            y: Math.random() * canvas.height,

            speedX:
                (Math.random() - 0.5) * 0.8,

            speedY:
                (Math.random() - 0.5) * 0.8,

            size:
                Math.random() * 2 + 1

        });

    }


    // Animation
    function animateCyber() {

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        // Draw particles
        particles.forEach(function(particle) {

            particle.x += particle.speedX;

            particle.y += particle.speedY;


            // Bounce from edges
            if (
                particle.x <= 0 ||
                particle.x >= canvas.width
            ) {

                particle.speedX *= -1;

            }


            if (
                particle.y <= 0 ||
                particle.y >= canvas.height
            ) {

                particle.speedY *= -1;

            }


            // Draw particle
            ctx.fillStyle = "#00e5ff";

            ctx.beginPath();

            ctx.arc(
                particle.x,
                particle.y,
                particle.size,
                0,
                Math.PI * 2
            );

            ctx.fill();

        });


        // Draw network lines
        for (
            let i = 0;
            i < particles.length;
            i++
        ) {

            for (
                let j = i + 1;
                j < particles.length;
                j++
            ) {

                const dx =
                    particles[i].x -
                    particles[j].x;


                const dy =
                    particles[i].y -
                    particles[j].y;


                const distance =
                    Math.sqrt(
                        dx * dx +
                        dy * dy
                    );


                if (distance < 130) {

                    ctx.beginPath();

                    ctx.strokeStyle =
                        "rgba(0, 229, 255, 0.18)";

                    ctx.lineWidth = 1;

                    ctx.moveTo(
                        particles[i].x,
                        particles[i].y
                    );

                    ctx.lineTo(
                        particles[j].x,
                        particles[j].y
                    );

                    ctx.stroke();

                }

            }

        }


        requestAnimationFrame(
            animateCyber
        );

    }


    animateCyber();


    // Resize screen
    window.addEventListener(
        "resize",
        function() {

            resizeCanvas();

        }
    );

}