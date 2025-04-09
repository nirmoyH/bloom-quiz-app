// main.js

let unlockedLevels = 1;

function checkAnswers(level) {
    const levelContainer = document.getElementById(`level-${level}`);
    const questions = levelContainer.querySelectorAll('[data-answer]');
    let score = 0;

    questions.forEach((q, i) => {
        const correct = q.getAttribute('data-answer');
        const selected = q.querySelector('input[type=radio]:checked');
        if (selected && selected.value === correct) {
            score++;
            selected.parentElement.classList.add('text-success');
        } else {
            if (selected) selected.parentElement.classList.add('text-danger');
        }
    });

    const result = levelContainer.querySelector('.result');
    result.innerHTML = `✅ You scored <strong>${score}/10</strong>`;

    // Unlock next level if score >= 7
    if (score >= 7 && level < 6) {
        const next = document.getElementById(`level-${level + 1}`);
        if (next) {
            next.classList.remove('locked');
            next.querySelector('.lock-msg').style.display = 'none';
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const submitButtons = document.querySelectorAll(".submit-btn");
    submitButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const level = parseInt(this.getAttribute("data-level"));
            checkAnswers(level);
        });
    });
});
