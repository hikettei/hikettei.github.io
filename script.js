const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");

const portraitButton = document.querySelector(".portrait-button");
let portraitTurns = 0;
if (!motionPreference.matches) {
  portraitButton.addEventListener("animationend", () => {
    portraitButton.classList.remove("is-intro");
  }, { once: true });
} else {
  portraitButton.classList.remove("is-intro");
}
portraitButton.addEventListener("click", () => {
  portraitButton.classList.remove("is-intro");
  portraitButton.style.animation = "none";
  portraitTurns += 1;
  const showQR = portraitTurns % 2 === 1;
  portraitButton.querySelector(".portrait-card").style.transform = `rotateY(${portraitTurns * 180}deg)`;
  portraitButton.setAttribute("aria-pressed", String(showQR));
  portraitButton.setAttribute("aria-label", showQR ? "Show portrait" : "Show QR code for https://hikettei.github.io/");
  portraitButton.querySelector(".portrait-front").setAttribute("aria-hidden", String(showQR));
  portraitButton.querySelector(".portrait-back").setAttribute("aria-hidden", String(!showQR));
});

const hero = document.querySelector(".hero");
const blog = document.querySelector(".writing");
let movingBetweenSections = false;

function moveBetweenSections(direction, event) {
  if (movingBetweenSections) {
    event.preventDefault();
    return true;
  }

  // On short screens, let the whole profile scroll into view first.
  const profileBottom = Math.max(0, hero.offsetHeight - window.innerHeight);
  const blogTop = blog.offsetTop;
  const goingDown = direction > 0 && window.scrollY >= profileBottom - 2 && window.scrollY < blogTop - 2;
  const goingUp = direction < 0 && window.scrollY > profileBottom + 2 && window.scrollY <= blogTop + 2;
  if (!goingDown && !goingUp) return false;

  event.preventDefault();
  movingBetweenSections = true;
  window.scrollTo({
    top: goingDown ? blogTop : 0,
    behavior: motionPreference.matches ? "instant" : "smooth",
  });
  // Absorb the rest of the wheel gesture while the section settles.
  window.setTimeout(() => { movingBetweenSections = false; }, motionPreference.matches ? 200 : 1000);
  return true;
}

window.addEventListener("wheel", (event) => {
  if (event.ctrlKey || event.defaultPrevented || Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
  moveBetweenSections(event.deltaY, event);
}, { passive: false });

let touchStart = null;
let touchConsumed = false;

window.addEventListener("touchstart", (event) => {
  touchStart = event.touches.length === 1 ? { x: event.touches[0].clientX, y: event.touches[0].clientY } : null;
  touchConsumed = false;
}, { passive: true });

window.addEventListener("touchmove", (event) => {
  if (!touchStart || event.touches.length !== 1 || event.defaultPrevented) return;
  const deltaY = touchStart.y - event.touches[0].clientY;
  const deltaX = touchStart.x - event.touches[0].clientX;
  if (touchConsumed) {
    event.preventDefault();
  } else if (Math.abs(deltaY) > 12 && Math.abs(deltaY) > Math.abs(deltaX)) {
    touchConsumed = moveBetweenSections(deltaY, event);
  }
}, { passive: false });

for (const eventName of ["touchend", "touchcancel"]) {
  window.addEventListener(eventName, () => { touchStart = null; }, { passive: true });
}

if (!motionPreference.matches && "IntersectionObserver" in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.remove("reveal-pending");
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12 });

  for (const element of document.querySelectorAll("[data-reveal]")) {
    if (element.getBoundingClientRect().top >= window.innerHeight) {
      element.classList.add("reveal-pending");
      observer.observe(element);
    }
  }

  motionPreference.addEventListener("change", () => {
    if (motionPreference.matches) {
      observer.disconnect();
      for (const element of document.querySelectorAll(".reveal-pending")) {
        element.classList.remove("reveal-pending");
      }
    }
  });
}
