$(document).ready(function() {
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const updateCart = debounce(function() {
        let cartId = $('#product-idx').val();
        let quantity = $('#cart-quantity-inputx').val();
        let quantity1 = $('#cart-quantity-input1x').val();
        let size = $('#size').val();
    
        // Synchronize the values of the input fields
        $('#cart-quantity-input').val(quantity);
        $('#cart-quantity-input1').val(quantity);
    
        console.log('Cart update triggered', { 'id': cartId, 'qty': quantity, 'size': size });
    
        $.ajax({
            url: "{% url 'store:update_product_quantity' %}",
            method: 'POST',
            data: {
                id: cartId,
                quantity: quantity,
                size: size,
                csrfmiddlewaretoken: "{{ csrf_token }}"
            },
            success: function(response) {
                console.log('Success response:', response);
                $('#new-price').text(`₦${response.total_price.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`);
                $('#new-price1').text(`₦${response.total_price.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`);
                $('#cart-quantity-input').val(response.qty);
                $('#cart-quantity-input1').val(response.qty);
            },
            error: function(response) {
                console.log('Error response:', response);
            }
        });
    }, 300); // Adjust debounce time as necessary
    
    $('#cart-quantity-input').off('change').on('change', function() {
        $('#cart-quantity-input1').val($(this).val());
        updateCart();
    });
    
    $('#cart-quantity-input1').off('change').on('change', function() {
        $('#cart-quantity-input').val($(this).val());
        updateCart();
    });
    
    function addToCart() {
        let productSlug = "{{ product.slug }}";
        console.log('Add to cart triggered', { 'slug': productSlug });

        $.ajax({
            url: "{% url 'store:add-to-cart' %}",
            method: 'POST',
            data: {
                slug: productSlug,
                csrfmiddlewaretoken: "{{ csrf_token }}"
            },
            success: function(response) {
                console.log('Success response:', response);
                $('#cart-count').html(response.cart_count);
                
                // Display messages using SweetAlert
                if (response.messages) {
                    response.messages.forEach(function(message) {
                        Swal.fire({
                            text: message.message,
                            icon: message.tags.includes('success') ? 'success' : 'error',
                            timer: 3000,
                            showConfirmButton: false
                        });
                    });
                } else {
                    console.log('No messages in response');
                }


                // Change button ID and text
               //$('#cart-btn').attr('id', 'delete-btn').text('Delete Cart');
                //$('#cart-btn1').attr('id', 'delete-btn1').text('Delete Cart');

                // Attach delete event
               // $('#delete-btn').off('click').on('click', deleteFromCart);
                //$('#delete-btn1').off('click').on('click', deleteFromCart);
            },
            error: function(response) {
                console.log('Error response:', response);
            }
        });
    }

    function deleteFromCart() {
        let productSlug = "{{ product.slug }}";
        console.log('Delete from cart triggered', { 'slug': productSlug });

        $.ajax({
            url: "{% url 'store:delete-from-cart' %}",
            method: 'POST',
            data: {
                slug: productSlug,
                csrfmiddlewaretoken: "{{ csrf_token }}"
            },
            success: function(response) {
                console.log('Success response:', response);
                $('#cart-count').html(response.cart_count);

                // Change button ID and text back to add to cart
                $('#delete-btn').attr('id', 'cart-btn').text('Add to Cart');
                $('#delete-btn1').attr('id', 'cart-btn1').text('Add to Cart');

                // Display messages using SweetAlert
                // Display messages using SweetAlert
                if (response.messages) {
                    response.messages.forEach(function(message) {
                        Swal.fire({
                            text: message.message,
                            icon: message.tags.includes('success') ? 'success' : 'error',
                            timer: 3000,
                            showConfirmButton: false
                        });
                    });
                } else {
                    console.log('No messages in response');
                }

                // Attach add event
                $('#cart-btn').off('click').on('click', addToCart);
                $('#cart-btn1').off('click').on('click', addToCart);
            },
            error: function(response) {
                console.log('Error response:', response);
            }
        });
    }

    // Attach initial add to cart event
    $('#cart-btn').off('click').on('click', addToCart);
    $('#cart-btn1').off('click').on('click', addToCart);   
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
