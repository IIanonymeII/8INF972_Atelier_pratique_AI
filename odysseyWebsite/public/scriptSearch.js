const unlogButton = document.getElementById('unlogButton');
const simulationButton = document.getElementById('launchSimulation')


unlogButton.addEventListener('click', function() {
  // Navigate to the search.html page
  window.location.href = 'home.html';
});

simulationButton.addEventListener('click', function() {
  // start and print the simulation
  simulationPan = document.getElementById('simulationResult');
  simulationPan.style.display = 'flex';
  //here the code getting the entrys and adapting the content
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
  var value1 = document.getElementById('value1');
  var value2 = document.getElementById('value2');
  
  slider.noUiSlider.on('update', function (values, handle) {
    if (handle === 0) {
      value1.innerHTML = Math.round(values[handle]);
    }
    if (handle === 1) {
      value2.innerHTML = Math.round(values[handle]);
    }
  });
});