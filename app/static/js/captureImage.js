// The buttons to start & stop stream and to capture the image
var btnStart = document.getElementById( "btn-start" );
var btnStop = document.getElementById( "btn-stop" );
var btnCapture = document.getElementById( "btn-capture" );

// The stream & capture
var stream = document.getElementById( "stream" );
var capture = document.getElementById( "capture" );
var snapshot = document.getElementById( "snapshot" );

// The video stream
var cameraStream = null;

// Attach listeners
if(btnStart){
    btnStart.addEventListener( "click", startStreaming );
}
if(btnStop){
    btnStop.addEventListener( "click", stopStreaming );
}
if(btnCapture){
    btnCapture.addEventListener( "click", captureSnapshot );
}

// Start Streaming
function startStreaming() {

	var mediaSupport = 'mediaDevices' in navigator;

    var x = document.getElementById("cam-display");
    if (x.style.display === "none") {
        x.style.display = "block";
    }

    var x = document.getElementById("stream-display");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
	if( mediaSupport && null == cameraStream ) {

		navigator.mediaDevices.getUserMedia( { video: true } )
		.then( function( mediaStream ) {

			cameraStream = mediaStream;

			stream.srcObject = mediaStream;

			stream.play();
		})
		.catch( function( err ) {

			console.log( "Unable to access camera: " + err );
		});
	}
	else {

		alert( 'Your browser does not support media devices.' );

		return;
	}
}

// Stop Streaming
function stopStreaming() {
    var x = document.getElementById("stream-display");
    if (x.style.display === "block") {
        x.style.display = "none";
    }
	if( null != cameraStream ) {

		var track = cameraStream.getTracks()[ 0 ];

		track.stop();
		stream.load();

		cameraStream = null;
	}
}

function captureSnapshot() {

	var x = document.getElementById("capture-display");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
	if( null != cameraStream ) {

		var ctx = capture.getContext( '2d' );
		var img = new Image();

		ctx.drawImage( stream, 0, 0, capture.width, capture.height );

		img.src		= capture.toDataURL( "image/png" );
		img.width	= 240;

		snapshot.innerHTML = '';

		snapshot.appendChild( img );
	}
}
