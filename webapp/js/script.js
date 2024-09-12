particlesJS("particles-js", {
    particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: "#8CC5D0" },
        shape: { type: "circle" },
        opacity: { value: 0.5, random: false },
        size: { value: 3, random: true },
        line_linked: { enable: true, distance: 150, color: "#8CC5D0", opacity: 0.4, width: 1 },
        move: { enable: true, speed: 6, direction: "none", random: false, straight: false, out_mode: "out", bounce: false }
    },
    interactivity: {
        detect_on: "canvas",
        events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" }, resize: true },
        modes: { repulse: { distance: 100, duration: 0.4 }, push: { particles_nb: 4 } }
    },
    retina_detect: true
});

document.addEventListener("DOMContentLoaded", () => {
    const title = document.querySelector('h1');
    title.style.opacity = 0;
    title.style.transform = 'translateY(-20px)';
    setTimeout(() => {
        title.style.transition = 'opacity 1s ease, transform 1s ease';
        title.style.opacity = 1;
        title.style.transform = 'translateY(0)';
    }, 300);

    // Remove the button event listeners from here, as they're now in dynamicPages.js

    // Rest of the JavaScript remains unchanged
});