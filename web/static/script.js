const socket = io.connect(window.location.origin);
// const socket = io.connect("http://localhost:5000")
const thresh = 0.5

socket.on('update_frame', function (data) {
    const imgElement = document.getElementById('cctv-stream');
    const confidenceElement = document.querySelector('.detection-info p');

    const imageBlob = new Blob([data.image], {type: 'image/jpeg'});
    const imageUrl = URL.createObjectURL(imageBlob);
    imgElement.src = imageUrl;
    
    if (data.confidence !== null) 
    {
        if (data.confidence >= thresh) 
        {
            confidenceElement.innerHTML += `<br>Confidence: ${data.confidence.toFixed(4)}, ${data.timestamp}`;
        }
        console.log(data.confidence.toFixed(4), data.timestamp)
    }
});

function connectToCCTV() {
    const url = document.getElementById('cctv_url').value.trim();
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');

    if (url) {
        console.log("url: ", url)
        socket.emit('start_cctv', { stream_url: url });

        imgElement.style.display = 'block';
        cctvContainer.style.display = 'flex';
    } else {
        alert('Please enter a valid CCTV URL.');
    }
    // socket.emit('start_cctv');

    // imgElement.src = "http://192.168.1.49:4747/video";
    // make the stream visible
    // imgElement.style.display = 'block';
    // cctvContainer.style.display = 'flex';
}

function disconnectCCTV()
{
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');

    imgElement.src = "";
    // make the stream visible
    imgElement.style.display = 'none';
    cctvContainer.style.display = 'none';

    socket.emit('stop_cctv');
    console.log("disconnect")
}

function uploadVideo() 
{
    const formData = new FormData();
    const videoFile = document.getElementById('video-file').files[0];
    const statusDiv = document.getElementById('upload-status');
    const videoContainer = document.getElementById('uploaded-video-container');
    const videoSource = document.getElementById('uploaded-video-source');

    if (!videoFile) 
    {
        alert("No video file selected!");
        return;
    }

    formData.append('video', videoFile);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) 
        {
            statusDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } 
        else 
        {
            statusDiv.innerHTML = `<p>${data.message}</p>`;
            videoSource.src = data.video_url;
            document.getElementById('uploaded-video').load();
            videoContainer.style.display = 'block';
        }
    })
    .catch(error => {
        statusDiv.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
    });
}

function switchContent(contentId) 
{
    var contentDivs = document.querySelectorAll('.content');
    contentDivs.forEach(function(div) 
    {
        div.style.display = 'none';
    });
    var selectedContent = document.getElementById(contentId);
    selectedContent.style.display = 'block';
}