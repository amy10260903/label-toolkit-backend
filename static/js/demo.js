import { userReport } from '/static/api/user.js';
import { uploadFile } from '/static/api/fingerprint.js';
import { getOptions } from '/static/api/option.js';
import { dragElement, resizeElement, updateElementPosition } from '/static/js/interact.js';
import { exportCSVFile } from '/static/js/export.js';

const results = {};
const dirname = 'mrt_music';
// const dirname = 'TW_TPE';
let ext = '.wav';
let req_id;
let req_time;

/**
 * GET options for select-list
 */
$( document ).ready(function() {
    getOptions()
        .then(function (response) {
            let options = JSON.parse(response.data.results);
            Object.keys(options).forEach(key => {
                options[key].forEach((val => {
                    let option = document.createElement("option");
                    option.text = val;
                    $(`#select-${key}`).append(option);
                }))
            })
            $('select').niceSelect();
        })
        .catch(function (response) {
            console.log(response);
        });
});

/**
 * UPDATE filename of uploaded audio track
 */
$('#upload-btn').change(function() {
    $('#upload-label')[0].textContent = this.files[0].name;
});

/**
 * EVENTS
 */
const Audio = {};
let onReady = false;
let tgl = true;
Audio.play = function() {
    Spectrum.play();
    $('#btn-stop')[0].disabled = false;
}
Audio.pause = function() {
    Spectrum.pause();
}
Audio.stop = function() {
    Spectrum.stop();
    $('#btn-stop')[0].disabled = true;
    if (!tgl) {
        $('#btn-play').find('i').toggleClass('fa-play fa-pause');
        tgl=!tgl;s
    }
}
Audio.toggle = function() {
    tgl?Audio.play():Audio.pause();
    $('#btn-play').find('i').toggleClass('fa-play fa-pause');
    tgl=!tgl;
}

$('#btn-play').click(Audio.toggle);
$('#btn-stop').click(Audio.stop);
$(window).keydown(function (e) {
    e.preventDefault();
    if (onReady) {
        if (e.keyCode == 0 || e.keyCode == 32) {
            $('#btn-play').click(); }
        else if (e.keyCode == 8 || e.keyCode == 46) {
             delSegment($('.current')[2].innerHTML); }
    }
})

$('#btn-add').click(function(){
    addSegment($('.current')[2].innerHTML);
});
$('#btn-export').click(function(){
    let filename = $('.current')[2].innerHTML;
    if (filename == 'Result') {
        alert('Please select a file!');
        return;
    }
    let label = $('#text-label').val();
    let headers = ['id', 'start', 'end', 'label'];
    exportCSVFile(headers, results[filename].timestamp, label, filename);

    const data = {
        request_id: req_id,
        filename: $(".current")[2].innerHTML,
        time: (Date.now()-req_time)/1000,
    }
    userReport(data)
        .then(function (response) {
            console.log('report submitted')
        })
        .catch(function (response) {
            console.log(response);
        });
});

Spectrum.on('ready', function() {
    $('#btn-play')[0].disabled = false;
    $('#btn-add')[0].disabled = false;
    onReady = true;
});

/**
 * INIT loaders
 */
$('.loader-inner').loaders();

const Loader = {};
Loader.show = function () {
    $('#loader')[0].style.display = 'block';
}
Loader.hide = function() {
    $('#loader')[0].style.display = 'none';
    $('#selection-form')[0].style.display = 'none';
    $('#candidate')[0].style.display = 'block';
    $('#label')[0].style.display = 'block';
    $('#export')[0].style.display = 'block';
}
Loader.audio = {};
Loader.audio.show = function () {
    $('#loader-audio')[0].style.display = 'block';
}
Loader.audio.hide = function() {
    $('#loader-audio')[0].style.display = 'none';
}

/**
 * POST analysis uploaded audio track
 */
function startAnalysis() {
    console.log('startAnalysis');
    // if ($(".current")[0].innerHTML=="Source" || $(".current")[1].innerHTML=="Sound event") {
    //     alert('Please select a dataset and an event!');
    //     return;
    // }
    if ($(".current")[0].innerHTML=="Source") {
        alert('Please select a dataset!');
        return;
    }
    const data = {
        category: $(".current")[0].innerHTML,
        file: $("#upload-btn").prop('files')[0],
        event: $(".current")[1].innerHTML,
    };
    Loader.show();
    // Loader.hide();
    // $.getJSON('/static/assets/json/results.json', function( json ) {
    //     // console.log(json);
    //     ext = json.extension;
    //     getLabel();
    //     getDetail(json.matched_result);
    //     updateSpectrum();
    // });
    uploadFile(data)
        .then(function (response) {
            let results = JSON.parse(response.data.results)
            ext = results.extension;
            req_id = response.data.request_id;
            Loader.hide();
            getLabel();
            getDetail(results.matched_result);
            updateSpectrum();
        })
        .catch(function (response) {
            console.log(response);
        });
}

/**
 * UPDATE list and show the results
 */
function getLabel() {
    let label = $("#upload-btn").val().split(/^.*[\\\/]/).pop().split('.').shift() || 'sound-event-name';
    // let label = $(".current")[1].innerHTML || 'sound-event-name';
    $('#text-label').attr('value', label);
}
function getDetail(data) {
    console.log(data);
    data.forEach((object) => {
        // selection menu
        let option = document.createElement("option");
        option.text = object.recording_name;
        $('#select-soundsource').append(option);

        // block for each segment
        let content = document.createElement("div");
        content.setAttribute("class", "content-segment");
        content.setAttribute("id", `content-segment-${object.recording_name}`);
        $('.wrapper').append(content);

        results[object.recording_name] = {
            'duration': 0,
            'timestamp': object.timestamp_in_seconds,
            'is_plot': false,
        };
    });
    $('select').niceSelect('update');
}

/**
 * UPDATE show corresponded spectrum of selected audio track
 */
function updateSpectrum() {
    const key = $('.current')[2].innerHTML;
    if (key=='Result') { return; }

    req_time = Date.now();
    Loader.audio.show();
    Spectrum.load(`/static/assets/dataset/${dirname}/${key}${ext}`);
    Spectrum.on('ready', function() {
        updateSegments($('.current')[2].innerHTML);
        Loader.audio.hide();
    });
}

/**
 * ADD candidate segments for selected audio track
 */
function updateSegments(key){
    // console.log('addSegment');
    $('.content-segment').each(function() {
        if (this.id == `content-segment-${key}`) {
            this.style.display = "block";
        } else {
            this.style.display = "none";
        }
    })
    if (!results[key].is_plot) {
        const duration = Spectrum.getDuration();
        results[key].duration = duration;
        results[key].timestamp.forEach((obj,idx) => {
            if (obj[0] < duration) {
                let segment = document.createElement("div"),
                    segment_drag = document.createElement("div");
                segment.setAttribute("class", "item");
                segment.setAttribute("id", `segment-${idx}`);
                segment.style.display = 'block';
                segment.style.left = (obj[0]/duration)*80 + 'vw';
                if (obj[1] > duration) {
                    segment.style.width = ((duration-obj[0])/duration)*80 + 'vw';
                } else {
                    segment.style.width = ((obj[1]-obj[0])/duration)*80 + 'vw';
                }
                segment_drag.setAttribute("class", "item-drag");
                segment.appendChild(segment_drag);
                $(`#content-segment-${key}`).append(segment);

                segment.addEventListener('click', function() {
                    let currentTime = Spectrum.getCurrentTime();
                    let currentProgress;
                    if (Math.round(currentTime*100)/100 == obj[0]) {
                        currentProgress = obj[1]/duration;
                    } else {
                        currentProgress = obj[0]/duration;
                    }
                    Spectrum.seekTo(currentProgress);

                    $('.item').each( function(idx) {
                        // console.log(id, idx);
                        this.classList.remove("item-focus");
                    });
                    this.classList.add("item-focus");
                    dragElement(this, key);
                    resizeElement(this, key);
                });
            }
        });
        results[key].is_plot = true;
    }
}
function addSegment(key) {
    $('.content-segment').each(function() {
        if (this.id == `content-segment-${key}`) {
            this.style.display = "block";
        } else {
            this.style.display = "none";
        }
    })
    const length = 5;
    const idx = $(`#content-segment-${key}`).children().length;
    const duration = Spectrum.getDuration(),
          current = Spectrum.getCurrentTime();
    let segment = document.createElement("div"),
        segment_drag = document.createElement("div");
    segment.setAttribute("class", "item");
    segment.setAttribute("id", `segment-${idx}`);
    segment.style.display = 'block';
    segment.style.left = (current/duration)*80 + 'vw';
    segment.style.width = (length/duration)*80 + 'vw';
    segment_drag.setAttribute("class", "item-drag");
    segment.appendChild(segment_drag);
    $(`#content-segment-${key}`).append(segment);

    updateElementPosition(segment, key);
    segment.addEventListener('click', function() {
        let currentProgress = current/duration;
        Spectrum.seekTo(currentProgress);

        $('.item').each( function(idx) {
            // console.log(id, idx);
            this.classList.remove("item-focus");
        });
        this.classList.add("item-focus");
        dragElement(this, key);
        resizeElement(this, key);
    });
}
function delSegment(key) {
    $(`#content-segment-${key}`).children().remove("div.item-focus");
}

export {
    startAnalysis,
    updateSpectrum,
    results,
};