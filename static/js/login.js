const formElement = document.getElementById('login-form')

function getCookie(name) {
    if (!document.cookie) {
        return null;
    }

    // Split document.cookie into an array of individual cookie strings
    const cookies = document.cookie.split(';');

    // Find the cookie that starts with the desired name
    const xsrfCookies = cookies
        .map(c => c.trim())
        .filter(c => c.startsWith(name + '='));

    // If the cookie is not found, return null
    if (xsrfCookies.length === 0) {
        return null;
    }

    // Return the decoded value of the cookie
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}


const login = async (event)=>{
    event.preventDefault()
    const csrfCookie = getCookie('csrftoken')
    const username = document.getElementById('identifier').value;
    const password = document.getElementById('password').value;
    const formData = {
        'username':username,
        'password':password,
    }
    console.log(formData)
    try{
        const response = await fetch('http://localhost:8000/account/login-user', {
        method: 'POST',
        headers: {
            'x-csrftoken':csrfCookie,
        },
        credentials: 'include',
        body: JSON.stringify(formData)
        })
        if(response.ok){
            data = await response.json()
            console.log(data)
            location.href = '/products/add'
        }
    }catch(error){
        console.log(`got an error: ${error}`)
    }
}

formElement.addEventListener('submit', login)