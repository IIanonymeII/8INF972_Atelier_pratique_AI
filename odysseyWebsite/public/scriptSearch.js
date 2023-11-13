const unlogButton = document.getElementById('unlogButton');
const simulationButton = document.getElementById('launchSimulation')


unlogButton.addEventListener('click', function() {
  // Navigate to the search.html page
  window.location.href = 'home.html';
});

simulationButton.addEventListener('click', function() {
  // Budget
  var budgetMin = document.getElementById('value1').innerHTML;
  var budgetMax = document.getElementById('value2').innerHTML;

  // Selected genres
  var selectedGenres = [];
  var checkboxes = document.querySelectorAll('input[name="group2"]:checked');
  checkboxes.forEach(function(checkbox) {
    var labelElement = checkbox.parentElement.querySelector('label');
    var labelText = labelElement.textContent;
    selectedGenres.push(labelText);
  });

  // Selected public
  var radioPublic = document.querySelector('input[name="group1"]:checked');
  var selectedPublic = radioPublic.parentElement.querySelector('label').textContent;

  // Selected goal
  var radioGoal = document.querySelector('input[name="group3"]:checked');
  var selectedGoal = radioGoal.parentElement.querySelector('label').textContent

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
  console.log(result);
  displayActors(result);
})
.catch(error => {
  console.error('Error:', error);
});

  // start and print the simulation
  simulationPan = document.getElementById('simulationResult');
  simulationPan.style.display = 'flex';

});


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
      budgetMin.innerHTML = Math.round(values[handle]);
    }
    if (handle === 1) {
      budgetMax.innerHTML = Math.round(values[handle]);
    }
  });
});

function displayActors(actors) {
  var ulElement = document.getElementById('listeDistribution');
  ulElement.innerHTML = '';// Clear any existing content

  actors.forEach(function(actor, index) {
      var liElement = document.createElement('li');
      liElement.id = 'elementActor';

      // Create div element
      var divElement = document.createElement('div');

      // Create img element
      var imgElement = document.createElement('img');
      
      //imgElement.src = "../../src/actorPictures/"+ actor+".png"
      imgElement.src = "/pictures/Acteur1.png";  // default if previous path does not exist
      
      // Create div for actor name
      var actorNameDiv = document.createElement('div');
      actorNameDiv.className = 'actorName';
      actorNameDiv.textContent = actor;
 
      divElement.appendChild(imgElement);
      divElement.appendChild(actorNameDiv);
      liElement.appendChild(divElement);
      ulElement.appendChild(liElement);
  });
}