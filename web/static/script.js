let frameBatch = [];
const BATCH_SIZE = 32;

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

function connectToCCTV() 
{
    const url = document.getElementById('textbox').value.trim();
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');
    const detectionInfo = document.querySelector('.detection-info p');

    if (url) 
    {
        imgElement.src = url;
        imgElement.style.display = 'block';
        cctvContainer.style.display = 'flex';

        setInterval(() => {
            fetch(url)
                .then((response) => response.blob())
                .then((blob) => {
                    const formData = new FormData();
                    formData.append('frame', blob, 'frame.jpg');
                    
                    fetch('/process_frame', {
                        method: 'POST',
                        body: formData,
                    })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.result) {
                            detectionInfo.innerHTML += `<br>${data.result}`;
                        } else if (data.error) {
                            detectionInfo.innerHTML += `<br>Error: ${data.error}`;
                        }
                    });
                });
        }, 62);
    } 
    else 
    {
        alert('Please enter a valid CCTV URL!');
        imgElement.style.display = 'none';
        cctvContainer.style.display = 'none';
    }
}

function processFrame() 
{
    const imgElement = document.getElementById('cctv-stream');
    const detectionInfo = document.querySelector('.detection-info p');

    if (!imgElement.src) 
    {
        alert('No frame available to process!');
        return;
    }

    const formData = new FormData();
    formData.append('frame', imgElement.src);

    fetch('/process_frame', {
        method: 'POST',
        body: formData,
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.result) 
        {
            detectionInfo.innerHTML += `<br>${data.result}`;
        } else if (data.error) 
        {
            detectionInfo.innerHTML += `<br>Error: ${data.error}`;
        }
    })
    .catch(error => {
        console.error('Fetch error:', error); // Debugging
        detectionInfo.innerHTML += `<br>Error: ${error}`;
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