const formElement = document.getElementById('add-product')

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

const addProduct = async (event)=>{
    event.preventDefault()
    const csrfCookie = getCookie('csrftoken')
    const productName = document.getElementById('name').value;
    const productDescription = document.getElementById('description').value;
    const productPrice = document.getElementById('price').value;

    try{
        const response = await fetch('http://localhost:8000/products/add-product', {
            method: 'POST',
            headers:{
                'x-csrftoken':csrfCookie,
            },
            credentials: 'include',
            body: JSON.stringify({
                'name':productName,
                'description':productDescription,
                'price':productPrice
            })
        })
        if(response.ok){
            const data = await response.json()
            console.log(data)
        }
    }catch(error){
        console.log(error)
    }
}
formElement.addEventListener('submit', addProduct)