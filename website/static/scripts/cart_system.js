// Cart functionality
$(document).ready(function () {

  function updateCount() {
    let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};
    let itemCount = Object.keys(itemsInCart).length;
    $('.count').text(itemCount);
    // Get item IDs to the server
    sendItemsToServer(itemsInCart);
    //updateTotalAmount(itemsInCart);
  }

  function updateQuantitiesInHTML(itemsInCart) {
    for (let itemId in itemsInCart) {
      if (itemsInCart.hasOwnProperty(itemId)) {
         console.log('itemsInCart[itemId]', itemsInCart[itemId])
        $('.item_quanity_number_' + itemId).val(itemsInCart[itemId].quantity);
      }
    }
  }

  function updateTotalAmount(itemsInCart) {
    let totalAmount = 0;
    for (let itemId in itemsInCart) {
      if (itemsInCart.hasOwnProperty(itemId)) {
        let itemDetails = itemsInCart[itemId];
        let itemQuantityInput = $(`.item_quantity_number_${itemId}`).val(itemDetails.product_qunatity.quantity)
        totalAmount += itemDetails.product_qunatity.quantity * itemDetails.product_price;
      }
    }

    // Update cart total in the main cart view
    $('.cart-total').text('$' + totalAmount.toFixed(2));
    displayItemsOnCartPage(itemsInCart);
  }

  function displayItemsOnCartPage(itemsInCart) {
    let itemDetailsHtml = '';
    if (Object.keys(itemsInCart).length > 0) {
      for (let itemId in itemsInCart) {
        let item = itemsInCart[itemId];
        price = item.product_qunatity.quantity * item.product_price
        itemDetailsHtml += `
         <li class="list-group-item d-flex justify-content-between lh-sm">
              <div class="d-flex justify-content-start">
                <div class="">
                  <img src="/static/uploads/${item.product_image}" width="60px" class="round>
                </div>
                <div class="">
                  <h6 class="mb-1">${item.product_title}</h6>
                  <span class="text-body-secondary fw-bold">$${price.toFixed(2)}</span>
                </div>
              </div>
              <span class="removeItem" data-item="${item.item_id}" class="ms-2 mt-4">
                <img src="/static/images/trash.png" width="30px" />
              </span>
          </li>
        `;
      }
      $('#itemDetails').html(itemDetailsHtml);
    } else {
      $('#itemDetails').html('<h5 style="color: red; margin: 10px 5px;">No item was selected. Add items to your cart.</h5>');
    }
  }

  // Handle adding items to the cart
  $('.addtocart').click(function () {
    let itemId = $(this).data('item');
    let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};

    if (itemsInCart[itemId]) {
      alert('Item already added');
    } else {
      // Add the new item to the cart
      itemsInCart[itemId] = {
        quantity: Number($(this).closest('.product-item').find('input').val()),
        product_title: $(this).closest('.product-item').find('h3').text(),
        product_image: $(this).closest('.product-item').find('img').attr('src'),
        product_price: parseFloat($(this).closest('.product-item').find('.price').text().replace('$', ''))
      };
      
      // Store the updated cart in localStorage
      localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
      updateCount();
      alert('Item successfully added to cart');
    }

    return false;
  });

  // Handle quantity increment
  $(document).on('click', '.quantity-right-plus', function () {
    console.log('Clicked')
    let itemId = $(this).data('item');
    console.log('itemId: ', itemId)
    let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};
    //const item_quantity = getElementByClass(`item_quanity_number_${itemId}`)
    let itemQuantityInput = $(`.item_quantity_number_${itemId}`);
    //let increamentVal;

    console.log('itemsInCart[itemId]', itemsInCart[itemId])

    if (itemsInCart[itemId]) {
      itemsInCart[itemId].quantity++;
      localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
      itemQuantityInput.val(itemsInCart[itemId].quantity);
      updateQuantitiesInHTML(itemsInCart);
      updateCount();
      //updateTotalAmount(itemsInCart);
    }
  });

  // Handle quantity decrement
  $(document).on('click', '.quantity-left-minus', function () {
    let itemId = $(this).data('item');
    let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};

    if (itemsInCart[itemId] && itemsInCart[itemId].quantity > 1) {
      itemsInCart[itemId].quantity--;
      localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
      updateQuantitiesInHTML(itemsInCart);
      //updateTotalAmount(itemsInCart);
      updateCount();
    }
  });

  // Handle item removal from the cart
  $(document).on('click', '.removeItem', function () {
    let itemId = $(this).data('item');
    console.log('itenId', itemId)
    let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};

    if (itemsInCart[itemId]) {
      delete itemsInCart[itemId];
      localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
      deleteItemsFromServer(itemId)
      updateCount();
      //updateTotalAmount(itemsInCart);
    }
  });

  // Update the server with current cart items
  function sendItemsToServer(itemsInCart) {
    $.ajax({
      url: '/fetch_cart_details',
      type: 'POST',
      data: JSON.stringify(itemsInCart),
      contentType: 'application/json',
      success: function(response) {
        displayItemsOnCartPage(response);
        updateTotalAmount(response);
      },
      error: function(xhr, status, error) {
        console.error('Error sending items to server:', error);
      }
    });
  }

  // Update the server with current cart items
  function deleteItemsFromServer(itemId) {
    $.ajax({
      url: '/delete_item',
      type: 'POST',
      data: {'item_id': itemId},
      contentType: 'application/json',
      success: function(response) {
        console.log('Response Recieved')
        updateCount();
        //displayItemsOnCartPage(response);
        //updateTotalAmount(response);
      },
      error: function(xhr, status, error) {
        console.error('Error sending items to server:', error);
      }
    });
  }

  // Call the updateCount function initially to populate the cart count
  updateCount();
});
