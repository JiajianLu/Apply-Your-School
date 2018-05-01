
window.onload = function(){ 
    // your code 
    var form = document.getElementById('file-form');
	var fileselect = document.getElementById('file-select');
	var uploadButton = document.getElementById('upload-button');
    form.onsubmit = function(event){
	var table_value = document.getElementById('sel1').value;
	event.preventDefault();
	uploadButton.innerHTML = 'Uploading...';
	
	//Get the selected files from the input
	var files = fileselect.files;

	//Create a new FormData object
	var formData = new FormData();
	formData.append('table',table_value)
	for(var i = 0; i< files.length; i++){
		var file = files[i];

		formData.append('file[]', file, file.name);
	}
	var request = new XMLHttpRequest();
	//request.open('POST', 'https://0.0.0.0:5001/import', true);
	// Set up a handler for when the request finishes.
	//request.send(formData);
	if (formData) {
	  $.ajax({
	    url: "/import",
	    type: "POST",
	    data: formData,
	    processData: false,
	    contentType: false,
	    success: function () {
	      uploadButton.innerHTML = 'Upload'; 
	    }
	  });
	}
	// request.onload = function () {
	// 	if (request.status === 200) {
	// 	// File(s) uploaded.
	// 		uploadButton.innerHTML = 'Upload';
	// 	} else {
	// 		alert('An error occurred!');
	// 	}
	// };
	
};
};//window.onload=
