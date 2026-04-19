let feedContainer = document.getElementById('feed');
let 

document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/getPosts')
        .then(response => response.json())
        .then(data => {
            loadFeed(data.posts);
        })
        .catch(err => {
            alert('Error: Unable to load feed. Please try again later.');
        })
});

//Function will be used to load the feed and post that every user makes
function loadFeed(posts) {
    feedContainer.innerHTML = '';
    posts.forEach(element => {
        feedContainer.innerHTML += `
        <div display="flex" flex-direction="column">
        <h3>${element.title}</h3>
        <small>By ${element.author} on ${element.date} </small>
        </div>
        <p>${element.content}</p>
        <div>
        ${loadComments(element.comments)}
        </div>
        `
    });
}

//This function will load the comments pertianing to each post
function loadComments(comments){
    let commentPage = `<div display="flex" flex-direction="column">
    <h4>Comments:</h4>`
    let commentContent = '';
    comments.forEach(element => {
        commentContent += `<div display="flex" flex-direction="column">
        <h5>${element.author} on ${element.date}</h5>
        <p>${element.content}</p>
        </div>`
    });
}