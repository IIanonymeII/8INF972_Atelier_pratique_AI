// Get the LOGIN div by its id
const loginButton = document.getElementById('loginButton');

// Add a click event listener to the LOGIN div
loginButton.addEventListener('click', goToSearchPage);

function goToSearchPage() {
    window.location.href = 'search.html';
}

let currentSection = 1;
buttons = document.getElementsByClassName("redirect-button")
for (var i = 0; i < buttons.length; i++) {
    var button = buttons[i];
    button.addEventListener("click", goToSearchPage)
}

window.addEventListener('wheel', (event) => {
    if (event.deltaY > 0) {
        // Scrolling down
        currentSection++;
    } else {
        // Scrolling up
        currentSection--;
    }

    if (currentSection < 1) {
        currentSection = 1;
    } else if (currentSection > 6) {
        currentSection = 6;
    }

    scrollToSection(currentSection);
});

function scrollToSection(section) {
    const sectionId = `section${section}`;
    const sectionElement = document.getElementById(sectionId);
    window.scrollTo({
        top: sectionElement.offsetTop,
        behavior: 'smooth'
    });
}

scrollToSection(currentSection);