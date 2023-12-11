const loadingAnimation = document.getElementById('pre-loader');
const simulationPanel = document.getElementById('simulationResult');
var minBudgetVal;
var maxBudgetVal;

document.addEventListener('DOMContentLoaded', function () {
  var slider = document.getElementById('slider');
  var values = [0, 1000000000]; // Initial values for the handles
  
  noUiSlider.create(slider, {
    start: values,
    connect: true,
    range: {
      'min': 0,
      'max': 1000000000
    }
  });
  
  // Display the values
  var budgetMin = document.getElementById('value1');
  var budgetMax = document.getElementById('value2');
  
  slider.noUiSlider.on('update', function (values, handle) {
    if (handle === 0) {
      number = Math.round(values[handle]);
      minBudgetVal = number
      budgetMin.innerHTML = formatNumber(number)
    }
    if (handle === 1) {
      number = Math.round(values[handle]);
      maxBudgetVal = number
      budgetMax.innerHTML = formatNumber(number)
    }
  });
});

function formatNumber(number) {
  if (number >= 0 && number < 1000) {
      return number.toString(); // Display raw number
  } else if (number >= 1000 && number < 100000) {
      return (number / 1000).toFixed(1) + ' k'; // Display number with 'k'
  } else if (number >= 100000 && number < 1000000000) {
      return (number / 1000000).toFixed(1) + ' M'; // Display number with 'M'
  } else  {
    return (number / 1000000000).toFixed(1) + ' B'; // Display number with 'M'
  }
}

let currentSlide = 1;

function nextSlide(i) {
  if (i == 2) {
    if (document.querySelectorAll('input[name="choice"]:checked').length == 0) {
      return
    }
  }
  if (i == 3) {
    console.log(document.getElementsByClassName("select")[0].children[0].textContent)
    if (document.getElementsByClassName("select")[0].children[0].textContent === "Select") {
      return
    }
  }
    const slideContainer = document.querySelector('.slide-container');
    currentSlide++;

    // Shift the container to the left to reveal the next slide
    slideContainer.style.transform = `translateX(-${(currentSlide - 1) * 100}vw)`;
}


document.addEventListener('DOMContentLoaded', function () {
  var dropdowns = document.querySelectorAll('.dropdown');

  dropdowns.forEach(function (dropdown) {
      dropdown.addEventListener('click', function () {
          this.setAttribute('tabindex', '1');
          this.classList.toggle('active');
          var menu = this.querySelector('.dropdown-menu');
          menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
      });

      dropdown.addEventListener('focusout', function () {
          this.classList.remove('active');
          var menu = this.querySelector('.dropdown-menu');
          menu.style.display = 'none';
      });

      var menuItems = dropdown.querySelectorAll('.dropdown-menu li');
      menuItems.forEach(function (item) {
          item.addEventListener('click', function () {
              var dropdown = this.closest('.dropdown');
              dropdown.querySelector('span').textContent = this.textContent;
              dropdown.querySelector('input').value = this.id;
          });
      });
  });
});


function selectImage(option) {
  const selectElement = document.getElementById('selectOption');
  selectElement.value = option;
  sendData()
}


function startLoading() {
  document.getElementById("form").style.display = 'none';
  document.getElementById("pre-loader").style.display = 'flex';
}

function stopLoading() {
  document.getElementById("pre-loader").style.display = 'none';
  simulationPanel.style.display = 'block'; 
}

function sendData() {
  
  // Budget
  var budgetMin = minBudgetVal
  var budgetMax = maxBudgetVal

  // Selected genres
  var selectedGenres = [];
  var checkboxes = document.querySelectorAll('input[name="choice"]:checked');
  checkboxes.forEach(function(checkbox) {
    var labelElement = checkbox.id
    labelText = document.getElementById(labelElement).labels[0].textContent
    
    selectedGenres.push(labelText);
  });

  // Selected public
  var radioPublic = document.getElementById("public-input").value
  var selectedPublic = document.getElementById(radioPublic).innerHTML

  // Selected goal
  var selectedID =  document.getElementById('selectOption').value
  selectedGoal = document.getElementById("option-image-" + selectedID).textContent

  // Log or use the retrieved values as needed
  console.log("Selected Budget Range:", budgetMin, "-", budgetMax);
  console.log("Selected Genres:", selectedGenres);
  console.log("Selected Public:", selectedPublic);
  console.log("Selected Objective:", selectedGoal);

  var data = {
    budgetMin: budgetMin,
    budgetMax: budgetMax,
    selectedGenres: selectedGenres,
    selectedPublic: selectedPublic,
    selectedGoal: selectedGoal
  };
  startLoading();

  // Make a POST request to your Python server
  fetch('http://localhost:5000/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(result => {
    startAnimation()
    console.log(result);
    setTimeout(function (){
      displayFilm(result.titre);
      displayDescription(result.description);
      displayActors(result.actors,result.img_actors);
      stopLoading();
                
    }, 2000); // How long you want the delay to be, measured in milliseconds.
    
    
  })
  .catch(error => {
    stopLoading();
    console.error('Error:', error);
  });
  
}

let currentSection = 1;

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

document.addEventListener('keydown', function(event) {
  // Check if the pressed key is the down arrow key (key code 40)
  if (event.key === 'ArrowDown') {
    currentSection++;
    if (currentSection < 1) {
      currentSection = 1;
    } else if (currentSection > 6) {
        currentSection = 6;
    }
    scrollToSection(currentSection);
  }
  if (event.key === 'ArrowUp') {
    currentSection--;
    if (currentSection < 1) {
      currentSection = 1;
    } else if (currentSection > 6) {
        currentSection = 6;
    }
    scrollToSection(currentSection);
  }
});

function startAnimation() {
  var container = document.getElementById('animationContainer');
  var image = document.getElementById('animatedImage');
  image.style.display= "inline-block";
  container.style.display = "inline-block";
  container.classList.add('animate');
  container.addEventListener("animationend", function() {
    container.classList.remove('animate'); // Remove animation class
    image.style.display = 'none'; // Hide the image
    container.style.display = "none";
  }, false);
  
}
function scrollToSection(section) {
  const sectionId = `section${section}`;
  const sectionElement = document.getElementById(sectionId);
  window.scrollTo({
      top: sectionElement.offsetTop,
      behavior: 'smooth'
  });
}

function displayFilm(titre) {

  // Utilisez querySelector pour obtenir le premier élément correspondant à la classe
  var titre_movie = document.getElementById("title")

  // Assurez-vous que l'élément est trouvé avant d'essayer de mettre à jour son contenu
  if (titre_movie) {
    titre_movie.innerHTML = '';
    titre_movie.textContent = titre;
  } else {
    console.error("Element with class 'titreSectionSimulation' not found.");
  }
}
function displayDescription(description) {

  // Utilisez getElementById pour obtenir l'élément par son ID
  var description_movie = document.getElementById("scenario");

  // Assurez-vous que l'élément est trouvé avant d'essayer de mettre à jour son contenu
  if (description_movie) {
    description_movie.innerHTML = '';
    description_movie.textContent = description;
  } else {
    console.error("Element with ID 'textSynopsis' not found.");
  }
}


function displayActors(actors,img_actor) {
  var container = document.getElementById('actors-container');
  container.innerHTML = '';// Clear any existing content

  actors.forEach(function(actor, index) {
      var current = document.createElement('div');
      current.classList.add("actor-container")
      // Create img element
      var imgElement = document.createElement('img');      
      imgElement.src = img_actor[index];  // default if previous path does not exist
      
      // Create div for actor name
      var actorNameDiv = document.createElement('p');
      actorNameDiv.textContent = actor;
 
      current.appendChild(imgElement);
      current.appendChild(actorNameDiv);
      container.appendChild(current);
  });
}