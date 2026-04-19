let searchBar = document.getElementById('userForm');
let searchInput = document.getElementById('userSearch');
let messageContainer = document.getElementById('MessageList');
let messageLogContainer = document.getElementById('MessagesLog'); 

searchBar.addEventListener('submit', function(event) {
    let theSearch = searchInput.ariaValueMax.trim();
    if (theSearch === '') {
        alert('Please enter a username to search for.');
    } else {
        fetch('/api/searchMessageLogs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ searchQuery: theSearch })
        })
        .then(response => response.json())
        .then(data => {
            loadMessages(data.messages)
        });
    }
})

//Used to load the messages that the user has with the specific user they searched for
function loadMessages(messages) {
    messageContainer.innerHTML = '';
    messages.forEach(element => {
        messageContainer.innerHTML += `
        <div display="flex" flex-direction="column">
        <h3>${element.username}</h3>
        </div>
        `
    });
}

function loadMessageLogs(logs){
    messageLogContainer.innerHTML = '';
    logs.forEach(element => {
        messageLogContainer.innerHTML += `
        <div display="flex" flex-direction="column">
        <h3>${element.username}</h3>
        <p>${element.message}</p>
        </div>
        `
    });
}