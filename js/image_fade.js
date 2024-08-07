$(document).ready(function() {    
  slideShow(10000);
});

function slideShow(speed) {
  // Remove the show class and set the opacity of all images to 0
  $('ul.images li').css({opacity: 0.0}).removeClass('show');
  
  // Display the first image
  $('ul.images li:first').css({opacity: 1.0}).addClass('show');
  
  // Start the gallery function to run the slideshow at the specified interval
  setInterval(gallery, speed);
}

var isAnimating = false;

function gallery() {
  if (isAnimating) return;
  isAnimating = true;

  // Get the current image
  var current = $('ul.images li.show');
  var next = current.next().length ? current.next() : $('ul.images li:first');

  // Exclude the current image from being modified
  $('ul.images li').not(current).css({opacity: 0.0}).removeClass('show');

  // Fade out the current image and fade in the next image simultaneously
  current.animate({opacity: 0.0}, 4000);
  next.css({opacity: 0.0}).addClass('show').animate({opacity: 1.0}, 4000, function() {
    // Cleanup after animation
    current.removeClass('show');
    isAnimating = false;
  });
}
