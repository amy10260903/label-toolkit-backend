const buttons = {
    play: document.getElementById("btn-play"),
    pause: document.getElementById("btn-pause"),
    stop: document.getElementById("btn-stop"),
    add: document.getElementById("btn-add")
};
const contents = {
    tag: document.getElementById("content-tag"),
    block: document.getElementById("content-block")
}
const slider = document.getElementById("slider");

let pos_mapping_to_tag = {};

// Handle Play button
buttons.play.addEventListener("click", function(){
    Spectrum.play();

    // Enable/Disable respectively buttons
    buttons.stop.disabled = false;
    buttons.pause.disabled = false;
    buttons.play.disabled = true;
}, false);

// Handle Pause button
buttons.pause.addEventListener("click", function(){
    Spectrum.pause();

    // Enable/Disable respectively buttons
    buttons.pause.disabled = true;
    buttons.play.disabled = false;
}, false);


// Handle Stop button
buttons.stop.addEventListener("click", function(){
    Spectrum.stop();

    // Enable/Disable respectively buttons
    buttons.pause.disabled = true;
    buttons.play.disabled = false;
    buttons.stop.disabled = true;
}, false);


// Handle Add button
// buttons.add.addEventListener("click", function(){
//     updateResult();
// }, false);

slider.addEventListener('input', function () {
    Spectrum.zoom(Number(this.value));
});

// Add a listener to enable the play button once it's ready
Spectrum.on('ready', function () {
    buttons.play.disabled = false;
});

// If you want a responsive mode (so when the user resizes the window)
// the spectrum will be still playable
window.addEventListener("resize", function(){
    // Get the current progress according to the cursor position
    let currentProgress = Spectrum.getCurrentTime() / Spectrum.getDuration();

    // Reset graph
    Spectrum.empty();
    Spectrum.drawBuffer();
    // Set original position
    Spectrum.seekTo(currentProgress);

    // Enable/Disable respectively buttons
    buttons.pause.disabled = true;
    buttons.play.disabled = false;
    buttons.stop.disabled = false;
}, false);