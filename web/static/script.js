function connectToCCTV() {
    const url = document.getElementById('textbox').value.trim();
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');
    const detectionInfo = document.querySelector('.detection-info p');

    if (url) {
        imgElement.src = url;
        imgElement.style.display = 'block';
        cctvContainer.style.display = 'flex';

        startCapturingFrames(detectionInfo);
    } else {
        alert('Please enter a valid CCTV URL!');
        imgElement.style.display = 'none';
        cctvContainer.style.display = 'none';
    }
}

function startCapturingFrames(detectionInfo) {
    setInterval(() => {
        captureFrame(detectionInfo);
    }, 400);
}

function captureFrame(detectionInfo) {
    const video = document.getElementById('cctv-stream');
    const canvas = document.createElement('canvas');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const dataURL = canvas.toDataURL('image/png');
    console.log(`Canvas Dimensions: ${canvas.width}x${canvas.height}`);
    console.log(`Video Dimensions: ${video.videoWidth}x${video.videoHeight}`);
    console.log(dataURL);
    sendFrameToServer(dataURL, detectionInfo);
}

function sendFrameToServer(dataURL, detectionInfo) {
    fetch('/cctv_infer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ frame: dataURL }),
    })
    .then(response => response.json())
    .then(data => {
        detectionInfo.innerHTML += `<br>${data.result}`;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
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