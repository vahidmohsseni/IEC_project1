'use strict';

/* globals MediaRecorder */

var room_name = null;

function uuid() { 
    function s4() {
      return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
  }

var uuid = uuid();


const mediaSource = new MediaSource();
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
let mediaRecorder;
let recordedBlobs;
let sourceBuffer;

const errorMsgElement = document.querySelector('span#errorMsg');
const recordedVideo = document.querySelector('video#recorded');
const recordButton = document.querySelector('button#record');
recordButton.addEventListener('click', () => {
  if (recordButton.textContent === 'Start Recording') {
    startRecording();
  } else {
    stopRecording();
    recordButton.textContent = 'Start Recording';
    playButton.disabled = false;
    downloadButton.disabled = false;
  }
});

const playButton = document.querySelector('button#play');
playButton.addEventListener('click', () => {
  const superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
  recordedVideo.src = null;
  recordedVideo.srcObject = null;
  recordedVideo.src = window.URL.createObjectURL(superBuffer);
  recordedVideo.controls = true;
  recordedVideo.play();
});

const downloadButton = document.querySelector('button#download');
downloadButton.addEventListener('click', () => {
  const blob = new Blob(recordedBlobs, {type: 'video/webm'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = 'test.webm';
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 100);
});

function handleSourceOpen(event) {
  console.log('MediaSource opened');
  sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
  console.log('Source buffer: ', sourceBuffer);
}

function handleDataAvailable(event) {
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}

function startRecording() {
  recordedBlobs = [];
  let options = {mimeType: 'video/webm;codecs=vp9'};
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
    console.error(`${options.mimeType} is not Supported`);
    errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
    options = {mimeType: 'video/webm;codecs=vp8'};
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.error(`${options.mimeType} is not Supported`);
      errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
      options = {mimeType: 'video/webm'};
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.error(`${options.mimeType} is not Supported`);
        errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
        options = {mimeType: ''};
      }
    }
  }

  try {
    mediaRecorder = new MediaRecorder(window.stream, options);
  } catch (e) {
    console.error('Exception while creating MediaRecorder:', e);
    errorMsgElement.innerHTML = `Exception while creating MediaRecorder: ${JSON.stringify(e)}`;
    return;
  }

  console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  recordButton.textContent = 'Stop Recording';
  playButton.disabled = true;
  downloadButton.disabled = true;
  mediaRecorder.onstop = (event) => {
    console.log('Recorder stopped: ', event);
  };
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start(10); // collect 10ms of data
  console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
  mediaRecorder.stop();
  console.log('Recorded Blobs: ', recordedBlobs);
}

function handleSuccess(stream) {
  recordButton.disabled = false;
  console.log('getUserMedia() got stream:', stream);
  window.stream = stream;

  const gumVideo = document.querySelector('video#gum');
  gumVideo.srcObject = stream;
}

async function init(constraints) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    getUserMediaSuccess(stream);
    handleSuccess(stream);
  } catch (e) {
    console.error('navigator.getUserMedia error:', e);
    errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
  }
}

document.querySelector('button#start').addEventListener('click', async () => {
//   const hasEchoCancellation = document.querySelector('#echoCancellation').checked;
  const constraints = {
    audio: {
      echoCancellation: {exact: false}
    },
    video: {
      width: 640, height: 360
    }
  };
  console.log('Using media constraints:', constraints);
  await init(constraints);
});


var localVideo = document.getElementById('gum');
var remoteVideo = document.getElementById('remoteVideo');
var peerConnectionConfig = {
    'iceServers': [
        {'urls': 'stun:stun.services.mozilla.com'},
        {'urls': 'stun:stun.l.google.com:19302'},
        {
        'urls': 'turn:turn.salar.click:3478?transport=udp',
        'credential': 'PASSWORD',
        'username': 'salar'
        },
    ]
};

let config = {
    iceServers: [
     {
         urls: "stun:stun.l.google.com:19302"
     },
     {
         urls: "turn:turn.winstonlcc.tk:3478",
         username: "ehsan",
         credential: "TaaBeTaa"
     }
   ]};


var peerConnection = new RTCPeerConnection(config);
peerConnection.onaddstream = gotRemoteStream;
peerConnection.onicecandidate = gotIceCandidate;    
peerConnection.ontrack = gotRemoteStream;
var constraints = {
    video: true
};

// if(navigator.mediaDevices.getUserMedia) {
//     navigator.mediaDevices.getUserMedia(constraints).then(getUserMediaSuccess).catch(errorHandler);
// } else {
//     alert('Your browser does not support getUserMedia API');
// }
function getUserMediaSuccess(stream) {
    console.log("getUserMediaSuccess");
    var localStream = stream;
    // localVideo.src = window.URL.createObjectURL(stream);
    peerConnection.addStream(localStream);
    if(0 == "{{isHost}}")
        peerConnection.createOffer().then(createdDescription).catch(errorHandler);
}
function gotIceCandidate(event) {
// alert("in ice cond");
    if(event.candidate != null) {
        //   alert("ingot ice %%%%%");
        // console.log("ingot ice %%%%%");
        //send_massage(JSON.stringify({'ice': event.candidate}) , "{{name}}", 'ice2');
        ws.send(JSON.stringify({type: 'ice', payload: {'ice': event.candidate, 'uuid': uuid, "room":"{{name}}"}}));
    }
}
function errorHandler(error) {
    console.log(error);
}
/*var source = new EventSource("/stream?channel="+"{{name}}");
source.addEventListener('request', gotRequest);
function gotRequest(event) {
    console.log("gotRequest");
    var data = JSON.parse(event.data);
    data =  JSON.parse(data.message);
    peerConnection.setRemoteDescription(new RTCSessionDescription(data.sdp)).then(function() {
        peerConnection.createAnswer().then(createdDescription).catch(errorHandler);
    }).catch(errorHandler);
}
source.addEventListener('ice1', gotIce);
function gotIce(event) {
    console.log("gotIce");
    var data = JSON.parse(event.data);
    data =  JSON.parse(data.message);
    peerConnection.addIceCandidate(new RTCIceCandidate(data.ice)).catch(errorHandler);
}
*/
//listenersss
// socket.on("sdp", function(data){
//     // console.log("in sdp data is ", data);
//     var json = JSON.parse(data);
//     // console.log("parsed is :", json.uuid );
//     if(json.uuid == uuid || json.room != "{{name}}")   return;
//     console.log("i got other side sdp message", data);
//     peerConnection.setRemoteDescription(new RTCSessionDescription(json.sdp)).then(function() {
//         peerConnection.createAnswer().then(createdDescription).catch(errorHandler);
//     }).catch(errorHandler);
// })

function on_sdp(data){
    // console.log("in sdp data is ", data);
    var json = JSON.parse(data);
    // console.log("parsed is :", json.uuid );
    if(json.uuid == uuid || json.room != "{{name}}")   return;
    console.log("i got other side sdp message", data);
    peerConnection.setRemoteDescription(new RTCSessionDescription(json.sdp)).then(function() {
        peerConnection.createAnswer().then(createdDescription).catch(errorHandler);
    }).catch(errorHandler);
};

// socket.on("ice", function(data){
//     console.log("in ice data is ", data);
//     var json = JSON.parse(data);
//     console.log("ice is :", json.ice );
//     if(json.uuid == uuid || json.room != "{{name}}")   return;
//     peerConnection.addIceCandidate(new RTCIceCandidate(json.ice)).catch(errorHandler);
// })

function on_ice(data){
    console.log("in ice data is ", data);
    var json = JSON.parse(data);
    console.log("ice is :", json.ice );
    if(json.uuid == uuid || json.room != "{{name}}")   return;
    peerConnection.addIceCandidate(new RTCIceCandidate(json.ice)).catch(errorHandler);
};
//test
// sendbySocket(JSON.stringify({'vaovao': "salamsalam", 'uuid': uuid}), "sdp");
function createdDescription(description) {
    console.log("createdDescription")
    peerConnection.setLocalDescription(description).then(function() {
        //  send_massage(JSON.stringify({'sdp': peerConnection.localDescription}) , "{{name}}", 'response');
        ws.send(JSON.stringify({type: 'sdp', payload:{'sdp': peerConnection.localDescription,
                                         'uuid': uuid, "room":"{{name}}"}}));
    }).catch(errorHandler);
}
function gotRemoteStream(event) {
    console.log('gotRemoteStream');
    remoteVideo.src = window.URL.createObjectURL(event.stream);
}
