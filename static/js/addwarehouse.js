const formElement = document.getElementById('add-warehouse')

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

const createWarehouse = async ()=>{
    const name = document.getElementById('name').value;
    const csrfCookie = getCookie('csrftoken')
    const warehouseAddress = await createAddress()
    let addressId = 0
    if(warehouseAddress){
        addressId = warehouseAddress.id
    }
    try{
        const response = await fetch('http://localhost:8000/warehouse/add-warehouse', {
            method: 'POST',
            headers:{
                'x-csrftoken':csrfCookie,
            },
            credentials: 'include',
            body:JSON.stringify({
                "name":name,
                "address_id":addressId
            })
        })
        if(response.ok){
            const data = await response.json();
            return data;
        }else{
            return null;
        }
    }catch(error){
        console.log(error)
        return null;
    }
}

const createAddress = async ()=>{
    const line1 = document.getElementById('line1').value
    const line2 = document.getElementById('line2').value
    const city = document.getElementById('city').value
    const state = document.getElementById('state').value
    const postalCode = document.getElementById('postal_code').value
    const country = document.getElementById('country').value
    const longitude = document.getElementById('longitude').value
    const latitude = document.getElementById('latitude').value
    const csrfCookie = getCookie('csrftoken')
    console.log(line1, line2, city, state, postalCode, country, longitude, latitude)
    try{
        const response = await fetch('http://localhost:8000/addresses/add', {
            method: 'POST',
            headers:{
                'x-csrftoken':csrfCookie,
                'Content-Type':'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                "line1":line1,
                "line2":line2,
                "city":city,
                "state":state,
                "country":country,
                "postal_code":postalCode,
                "latitude":latitude,
                "longitude":longitude,
            })
        })
        if(response.ok){
            const data = response.json()
            return data;
        }else{
            return null;
        }
    }catch(error){
        return null
    }
}

const addWareHouse = async (event)=>{
   event.preventDefault() 
   const warehouse = await createWarehouse()
   if(warehouse){
        console.log(warehouse)
        location.href='/'
   }
}

formElement.addEventListener('submit', addWareHouse)