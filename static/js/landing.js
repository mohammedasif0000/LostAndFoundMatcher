document.addEventListener("DOMContentLoaded", () => {

    let seconds = 5;

    const counter = document.getElementById("counter");

    counter.textContent = "05";

    const timer = setInterval(() => {

        seconds--;

        if (seconds > 0) {
            counter.textContent = String(seconds).padStart(2, "0");
        }

        if (seconds <= 0) {

            clearInterval(timer);

            document.body.classList.add("leaving");

            setTimeout(() => {
                window.location.href = "/black";
            }, 700);
        }

    }, 1000);

});