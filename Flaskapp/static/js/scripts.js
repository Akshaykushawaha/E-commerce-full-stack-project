function addToCart(productId) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `product_id=${productId}&quantity=1`
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Product added to cart!');
        } else {
            alert(data.message);
            window.location.href = '/login';
        }
    })
    .catch(error => console.error('Error:', error));
}

function removeFromCart(productId) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            alert('Product removed from cart!');
            window.location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}
