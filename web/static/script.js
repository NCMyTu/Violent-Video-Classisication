const socket = io.connect(window.location.origin);
// const socket = io.connect("http://localhost:5000")
const thresh = 0.5

socket.on('update_frame', function (data) 
{
    const imgElement = document.getElementById('cctv-stream');
    const confidenceElement = document.querySelector('.detection-info p');

    const imageBlob = new Blob([data.image], {type: 'image/jpg'});
    const imageUrl = URL.createObjectURL(imageBlob);
    imgElement.src = imageUrl;
    
    if (data.is_prediction) 
    {
        if (data.prediction == 1) 
        {
            confidenceElement.innerHTML += `<br>[${data.timestamp}] Detected violence, conf: ${data.confidence.toFixed(4)}`;
        }
        console.log(`[${data.timestamp}] pred: ${data.prediction}, conf: ${data.confidence.toFixed(4)}`)
    }
});

function connectToCCTV() 
{
    const url = document.getElementById('cctv_url').value.trim();
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');

    if (url) 
    {
        console.log("url: ", url)
        socket.emit('start_cctv', { stream_url: url });

        imgElement.style.display = 'block';
        cctvContainer.style.display = 'flex';
    } 
    else 
    {
        alert('Please enter a valid CCTV URL.');
    }
}

function disconnectCCTV()
{
    const imgElement = document.getElementById('cctv-stream');
    const cctvContainer = document.querySelector('.cctv-container');
    const confidenceElement = document.querySelector('.detection-info p');

    imgElement.src = "";
    imgElement.style.display = 'none';
    cctvContainer.style.display = 'none';
    confidenceElement.innerHTML = "";

    socket.emit('stop_cctv');
    console.log("disconnect");
}

function uploadVideo() 
{
    const formData = new FormData();
    const videoFile = document.getElementById('video-file').files[0];
    const videoContainer = document.getElementById('uploaded-video-container');
    const videoSource = document.getElementById('uploaded-video-source');
    const videoPredContainer = document.getElementById('video-prediction');

    if (!videoFile) 
    {
        alert("No video file selected!");
        return;
    }

    formData.append('video', videoFile);

    fetch('/upload_video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        videoSource.src = data.video_url;
        document.getElementById('uploaded-video').load();
        videoContainer.style.display = 'block';
        videoPredContainer.style.display = 'none';
    })
}

function predictVideo()
{
    const videoContainer = document.getElementById('uploaded-video-container');
    const videoPredContainer = document.getElementById('video-prediction')
    const videoPredP = document.querySelector('#video-prediction p')

    videoPredContainer.style.display = 'none';

    if (!videoContainer.style.display || videoContainer.style.display === 'none') 
    {
        alert("No video has been uploaded yet!");
        return;
    }
    
    fetch('/predict_video', {
        method: 'POST',
        body: JSON.stringify({ video_url: document.getElementById('uploaded-video-source').src }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        videoPredContainer.style.display = "flex";

        if (data.label == 1) 
        {
            videoPredP.innerHTML = `<span style="color: red;">Violent</span>${'&nbsp;'.repeat(15)}conf_score: ${data.conf_score.toFixed(4)}`;
        } 
        else 
        {
            videoPredP.innerHTML = `<span style="color: green;">Non-violent</span>${'&nbsp;'.repeat(15)}conf_score: ${data.conf_score.toFixed(4)}`;
        }
    });
}

function switchContent(contentId, clickedLink) 
{
    var contentDivs = document.querySelectorAll('.content');
    contentDivs.forEach(function(div) 
    {
        div.style.display = 'none';
    });

    var selectedContent = document.getElementById(contentId);
    selectedContent.style.display = 'block';

    var links = document.querySelectorAll('.sidenav a');
    links.forEach(function(link) {
        link.style.backgroundColor = '#333';
        link.style.color = '#818181';
    });

    clickedLink.style.color = '#f1f1f1';   
    clickedLink.style.backgroundColor = '#575757';
}