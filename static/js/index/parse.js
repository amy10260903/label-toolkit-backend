const selection = {
	'location': document.getElementById('select-location'),
	'place': document.getElementById('select-place'),
	'soundsource': document.getElementById('select-soundsource'),
};

$(document).ready(function () {
	$.get('/assets/dataset/location.yaml', function( text ) {
		let obj = jsyaml.load( text );
		for(let key in obj){
			for (i=0; i<obj[key].length; i++) {
				let option = document.createElement("option");
				if (key == 'location') {
					option.text = obj[key][i].country + ' / ' + obj[key][i].city;
				} else {
					option.text = i + ' : ' + obj[key][i];
				}
				selection[key].add(option);	
			}
		}
		$('select').niceSelect();
	});
});