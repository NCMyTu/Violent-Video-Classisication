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

function connectToCCTV() {
    const url = document.getElementById('textbox').value.trim();
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');
    const detectionInfo = document.querySelector('.detection-info p');

    if (url) {
        imgElement.src = url;
        imgElement.style.display = 'block';
        cctvContainer.style.display = 'flex';
        setInterval(() => {
            fetch('/cctv_infer', {
                method: 'POST',
                body: JSON.stringify({ cctv_url: url }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.text())  // the response is a string
            .then(data => {
                detectionInfo.innerHTML += `<p>${data}</p>`;
            })
            .catch(error => console.error(error));
        }, 62);
    } else {
        alert('Please enter a valid CCTV URL!');
        imgElement.style.display = 'none';
        cctvContainer.style.display = 'none';
    }
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