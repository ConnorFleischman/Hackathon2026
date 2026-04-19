let profileInfo = document.getElementById('profile-info');
let myPosts = document.getElementById('my-posts');


//As soon as the page renders, we will load the users profile information and their posts
document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/getProfileInfo')
        .then(response => response.json())
        .then(data => {
            loadProfileInfo(data.profile);
            loadMyPosts(data.posts);
        })
        .catch(err => {
            alert('Error: Unable to load profile information. Please try again later.');
        })
});

//This function loads the info for the users profile such as their username, name, email, and bio. This will be used to populate the profile page with the users information
function loadProfileInfo(profile) {
    profileInfo.innerHTML = `
    <h2>${profile.username}</h2>
    <p>Name: ${profile.name}</p>
    <p>Email: ${profile.email}</p>
    <p>Bio: ${profile.bio}</p>
    `
}


//This loads the post pertaining to the user that is logged in
function loadMyPosts(posts) {
    myPosts.innerHTML = '<h3>My Posts:</h3>';
    posts.forEach(element => {
        myPosts.innerHTML += `
        <div style="display: flex; flex-direction: column;">
        <h4>${element.title}</h4>
        <small>Posted on ${element.date} </small>
        </div>
        <p>${element.content}</p>
        `
    });
}