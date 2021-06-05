const selection = {
	'location': document.getElementById('select-location'),
	'place': document.getElementById('select-place'),
	'soundsource': document.getElementById('select-soundsource'),
};

$(document).ready(function () {
	$.getJSON('/assets/dataset/json/data.json', function( json ) {
		let obj = json;
		for(let key in obj){
			if (key == 'category') {
				for (i=0; i<obj[key].length; i++) {
					let option = document.createElement("option");
					option.text = obj[key][i];
					selection['location'].add(option);	
				}
			}
			// } else if (key == 'target') {
			// 	for (i=0; i<obj[key].length; i++) {
			// 		let option = document.createElement("option");
			// 		option.text = obj[key][i];
			// 		selection['place'].add(option);	
			// 	}
			// }
		}
		$('select').niceSelect();
	});
});

function updateResult() {
	let select_location = document.getElementsByClassName("current")[0].innerHTML;
	let select_place = document.getElementsByClassName("current")[1].innerHTML;
	
	selection['soundsource'].length = 1;
	$.getJSON('/assets/dataset/json/'+select_location+'/'+select_place+'.json', function( json ) {
		let obj = json;
		for(let key in obj){
			if (key == 'results') {
				for (i=0; i<obj[key].length; i++) {
					let option = document.createElement("option");
					option.text = obj[key][i].song_name;
					selection['soundsource'].add(option);	
					results[obj[key][i].song_name] = obj[key][i].offset_seconds;
				}
			}
		}
		console.log(results);
		$('select').niceSelect('update');
	});
}

function updateSpectrum() {
	let select_location = document.getElementsByClassName("current")[0].innerHTML;
	let select_sndsrc = document.getElementsByClassName("current")[1].innerHTML;

	Spectrum.load('/assets/dataset/TW_TPE/'+select_sndsrc+'.wav');
	let currentTime = parseInt(results[select_sndsrc]);
	if (currentTime < 0 ) {
		currentTime = 0;
	}
	console.log(currentTime);
	console.log(Spectrum.getDuration());
	let currentProgress = currentTime / Spectrum.getDuration();
	console.log(currentProgress);
	Spectrum.seekTo(currentProgress);

}