"use strict";
const player = videojs("videoPlayer", {
  controls: true,
  autoplay: false,
  preload: "auto",
  disablePictureInPicture: true,
  muted: true,
  controlBar: {
    volumePanel: false,
    remainingTimeDisplay: {
      displayNegative: false
    },
    skipButtons: {
      forward: 10,
      backward: 10
    }
  },
  playbackRates: [1.0, 1.5, 2.0, 2.5, 3.0],
  userActions: {
    hotkeys: true
  },
  plugins: {
    hotkeys: {
      enableMute: false,
      enableVolumeScroll: false,
      seekStep: 30,
    }
  }
});
const addObservationButton = $("#addObservationButton");
const markFinishedButton = $("#markFinishedButton");
const modalAddObservation = new bootstrap.Modal(document.getElementById("addObservationModal"));

// FIXME: the event below doesn't seem to work to set the video position.
const urlParams = new URLSearchParams(window.location.search);
const position = urlParams.get("position");
player.on("loadedmetadata", function () {
  if (position !== null) {
    // Start the player at the requested position.
    console.log("Starting at position " + position);
    player.currentTime(position);
  }
});

player.on("pause", () => {
  // Copy the video position value to the model form field.
  $("#videoPosition").val(Math.floor(player.currentTime()));
});

// On completion of the video, enable the 'Mark finished' button.
player.on("ended", function () {
  markFinishedButton.prop("disabled", false);
});

markFinishedButton.on("click", function () {
  // We have to set the CSRF token for this AJAX request.
  // https://docs.djangoproject.com/en/dev/howto/csrf/#setting-the-token-on-the-ajax-request
  $.ajax({
    headers: {
      "X-CSRFToken": markFinishedButton.data("csrf-token")
    },
    type: "PATCH",
    url: markFinishedButton.data("action"),
    dataType: "json",
    success: function () {
      // Change the text of the 'Mark finished' button, and disable it.
      markFinishedButton.html("Finished!");
      markFinishedButton.prop("disabled", true);
    }
  });
});

// On clicking 'Add Observation', pause the player.
// The HTML button is wired to display the modal popup.
addObservationButton.on("click", function () {
  player.pause();
});

// Function fired upon clicking the submit button in the 'Add observation' form.
function submitObservationForm(form) {
  // Submit the form via AJAX.
  const saveForm = $("#saveObservationForm");
  $.ajax({
    type: "POST",
    url: saveForm.attr("action"),
    data: saveForm.serialize(),
    dataType: "json",
    success: function (response) {
      // Success notification.
      Toastify({
        text: "New penguin observation created at position " + response.position,
        duration: 1500
      }).showToast();
      // Reset the form fields.
      form.reset();
      // Hide the modal.
      modalAddObservation.hide();
      // Resume playing the video.
      player.play();
      // Trigger the videoObservationsTable htmx element event.
      document.body.dispatchEvent(new Event("observationCreated"));
    }
  });
}
