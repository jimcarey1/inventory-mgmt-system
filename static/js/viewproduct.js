const formElement = document.getElementById('product-to-warehouse')

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

const addProductToWarehouse = async (event) => {
    event.preventDefault()
    const warehouse = document.getElementById('warehouse_id').value;
    const product = document.getElementById('product_id').value;
    const quantity = document.getElementById('quantity').value;
    const csrfCookie = getCookie('csrftoken')

    try{
        const response = await fetch('http://localhost:8000/inventory/add', {
            method: 'POST',
            headers:{
                'Content-Type':'application/json',
                'x-csrftoken': csrfCookie,
            },
            credentials: 'include',
            body: JSON.stringify({
                "product_id":product,
                "warehouse_id":warehouse,
                "quantity":quantity
            })
        })
        if(response.ok){
            location.reload()
        }
    }catch(error){
        console.log(error)
    }
}
formElement.addEventListener('submit', addProductToWarehouse)