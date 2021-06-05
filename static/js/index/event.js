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
buttons.add.addEventListener("click", function(){
    let select_sndsrc = document.getElementsByClassName("current")[2];
    if (select_sndsrc.innerHTML.includes(":")) {
        let currentProgress = Spectrum.getCurrentTime() / Spectrum.getDuration();
        let item = {};

        for(let key in contents){
            item[key] = document.createElement("div");
            item[key].setAttribute("class", "item");
            contents[key].appendChild(item[key]);

            item[key].style.display = 'block';
            item[key].style.left = (currentProgress*80) + 'vw';
            pos_mapping_to_tag[item[key].style.left] = {};
            pos_mapping_to_tag[item[key].style.left]['start'] = currentProgress;
            pos_mapping_to_tag[item[key].style.left]['end'] = currentProgress+60/(window.innerWidth*0.8);
            
            if (key == 'tag') {
                item[key].innerHTML = select_sndsrc.innerHTML.split(' : ')[0] + ' <span class="hide"><i class="fa fa-close"></i></span>';
                pos_mapping_to_tag[item[key].style.left][key] = item[key];
                
                item[key].addEventListener("click", function(){
                    if (pos_mapping_to_tag[this.style.left]) {
                        currentProgress = pos_mapping_to_tag[this.style.left].end;
                        Spectrum.seekTo(currentProgress);
                    }
                }, false);

                item['close'] = item[key].childNodes[1];
                pos_mapping_to_tag[item[key].style.left]['close'] = item['close'];
                
                item['close'].addEventListener("click", function(){
                    pos_mapping_to_tag[this.parentNode.style.left].block.remove();
                    this.parentNode.remove();
                    delete pos_mapping_to_tag[this.parentNode.style.left];
                }, false);

            } else {
                pos_mapping_to_tag[item[key].style.left][key] = item[key];
                item[key].addEventListener("click", function(){
                    if (pos_mapping_to_tag[this.style.left]) {
                        currentProgress = pos_mapping_to_tag[this.style.left].start;
                        Spectrum.seekTo(currentProgress);
                        this.classList.toggle("item-focus");
                    }
                }, false);
                new ResizeSensor(item[key], function(){ 
                    var percentage = parseInt(item[key].style.width,10)/(window.innerWidth*0.8);
                    if (!isNaN(percentage)) {
                        pos_mapping_to_tag[item[key].style.left]['end'] = currentProgress+percentage;
                    }
                });
            }
        }
    }
}, false);


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