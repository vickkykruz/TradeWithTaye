// Cart functionality
      $(document).ready(function () {

        function updateCount() {
          let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};
          let itemCount = Object.keys(itemsInCart).length;
          $('.count').text(itemCount);

          // Get item IDs to the server
          sendItemsToServer(itemsInCart);
        }

        // Function to update quantities in HTML
        function updateQuantitiesInHTML(itemsInCart) {
          // Iterate through itemsInCart object
          for (let itemId in itemsInCart) {
            if (itemsInCart.hasOwnProperty(itemId)) {
              // Output the quantity in the corresponding HTML element
              // $('.item_quanity_number_' + itemId).text(itemsInCart[itemId]);
              $('.item_quanity_number_' + itemId).text(itemsInCart[itemId]);
              console.log($('.item_quanity_number_' + itemId));
            }
          }
        }

        updateCount();
        $(document).on('click', '.addQuantity', function () {
          let itemId = $(this).data('item');

          // Retrieve existing items from local storage
          let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};
          itemsInCart[itemId] = (itemsInCart[itemId] || 0) + 1;
          localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
          
          // Output the quantity in an HTML template
          $('.item_quanity_number_' + itemId).text(itemsInCart[itemId]);
          sendItemsToServer(itemsInCart);
        });

        $(document).on('click', '.removeQuantity', function () {
          let itemId = $(this).data('item');

          // Retrieve existing items from local storage
          let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};
          if (itemsInCart[itemId] && itemsInCart[itemId] > 1) {
            itemsInCart[itemId]--;
          }
          localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));

          // Output the quantity in an HTML template
          $('.item_quanity_number_' + itemId).text(itemsInCart[itemId]);
          sendItemsToServer(itemsInCart);
        });

        $(document).on('click', '.removeItem', function () {
          let itemId = $(this).data('item');

          // Retrieve current items from localStorage
          let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};

          // Check if the item exists in localStorage
          if (itemsInCart.hasOwnProperty(itemId)) {

            // Send the remove Id to the server
            $.ajax({
              url: '/delete_item',
              type: 'POST',
              data: {'item_id': itemId},
              success: function (response) {
                console.log(response)
                // Remove the item corresponding to the given itemId
                delete itemsInCart[itemId];

                // Update localStorage with the modified items
                localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
                let updatedItemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {}
                sendItemsToServer(updatedItemsInCart);
                updateCount();
              },
              error: function(xhr, status, error) {
                console.error(error)
              }
            })
          }
        });

        $("#openModalBtn").click(function() {
          let startTime = new Date();
          startTime.setMinutes(startTime.getMinutes() + 60);
          let alertDisplayed = false;

          let intervalId = setInterval(function() {
            let currentTime = new Date();
            let elapsedTime = Math.floor((startTime - currentTime) / 1000);

            if (currentTime >= startTime && !alertDisplayed) {
              alert("Service time out");
              alertDisplayed = true;
              clearInterval(intervalId);
            }

            if (!alertDisplayed) {
              $("#timeDisplay").html(formatTime(elapsedTime));
            } else {
              $("#timeDisplay").html("0min 0sec");
            }

          }, 1000);
          function formatTime(seconds) {
            let hours = Math.floor(seconds / 3600);
            let mintues = Math.floor((seconds % 3600) / 60);
            // let mintues = Math.floor(seconds / 60);
            let remainingSeconds = Math.floor(seconds % 60);

            // return mintues + "min " + remainingSeconds + "sec";
            return hours + "hr " + mintues + "min " + remainingSeconds + "sec";
          }

          $("#close_pay").click(function() {
            clearInterval(intervalId);
          })
        })

        $('.addtocart').unbind('click').click(function () {
          let itemId = $(this).data('item');

          // Rerieve existing items from location storage or initialize an empty array
          let itemsInCart = JSON.parse(localStorage.getItem('itemsInCart')) || {};

          if (itemsInCart[itemId]) {
           alert('Item already added');
          } else {
            // Add the new item to the itemsInCart array
            itemsInCart[itemId] = 1;

            // Store the updated itemInCart
            localStorage.setItem('itemsInCart', JSON.stringify(itemsInCart));
            updateCount();
            alert('Successfully added item to cart');

             // Send item IDs to the server
            sendItemsToServer(itemsInCart);
            updateQuantitiesInHTML(itemsInCart);
          }
          return false;
       });

        // Fetch the items and pass it to the serve for validation and getting the contant
        function sendItemsToServer(itemsInCart) {
          $.ajax({
            url: '/fetch_cart_details',
            type: 'POST',
            data: JSON.stringify(itemsInCart),
            contentType: 'application/json',
            success: function(response) {
              console.log('Items sent to server successfully');
              displayItemsOnCartPage(response)
              displayItemsOnAsideBar(response)
              updateQuantitiesInHTML(itemsInCart);
              // Optionally handle the server response here
            },
            error: function(xhr, status, error) {
              console.error('Error sending items to server:', error);
              // Optionally handle the error here
            }
          });
        }

        function displayItemsOnCartPage(itemDetails) {
          let itemDetailsHtml = '';
          if (itemDetails.length != 0) {
            $.each(itemDetails, function(index, item) {
              itemDetailsHtml += '<div class="item-container" style="justify-content: start;">';
              itemDetailsHtml += '<div class="item-image">';
               itemDetailsHtml += '<img src="/static/uploads/' + item.product_image + '" class="img-fluid" style="width: 150px; height: 150px;" alt="">';
              itemDetailsHtml += '</div>';
              itemDetailsHtml += '<div class="item-content" style="width: 100%;">';
              itemDetailsHtml += '<h3 class="item-title">' + item.product_title + '</h3>';
              itemDetailsHtml += '<hr>';
              itemDetailsHtml += '<div class="cart-amount">';
              itemDetailsHtml += '<h5>Item Price: &#8358; ' + item.product_price.toFixed(2) + '</h5>';
              itemDetailsHtml += '<div class="cart-qunatity">';
              itemDetailsHtml += '<h5>Quantity</h5>';
              itemDetailsHtml += '<div class="item-quanity">';
              itemDetailsHtml += '<button class="addQuantity" data-item="' + item.item_id + '">&plus;</button>';
              itemDetailsHtml += '<p>' + item.product_qunatity + '</p>';
              itemDetailsHtml += '<button class="removeQuantity" data-item="' + item.item_id + '" type="button">&minus;</button>';
              itemDetailsHtml += '</div>';
              itemDetailsHtml += '</div>';
              itemDetailsHtml += '</div>';
              itemDetailsHtml += '<hr style="margin-top: 10px;">';
              itemDetailsHtml += '<span class="removeItem" data-item="' + item.item_id + '" style="float: right;"><i class="bx bx-trash rm-item-btn"></i></span>';
              itemDetailsHtml += '</div>';
              itemDetailsHtml += '</div>';
           });
           $('#itemDetails').html(itemDetailsHtml);
         } else {
           itemDetailsHtml += '<h5 style="color: red; margin: 10px 5px;">No item was selected ): Add your item to cart </h5>';
           $('#itemDetails').html(itemDetailsHtml);
         }
       }

        function displayItemsOnAsideBar(itemDetails) {
          let itemDetailsHtml = '';
          let totalAmtHtml = '';
          let totalPrice = 0;
          $.each(itemDetails, function(index, item) {
            itemDetailsHtml += '<div class="selected-item">';
            itemDetailsHtml += '<div class="selected-item-img">';
            itemDetailsHtml += '<img src="/static/uploads/' + item.product_image + '" style="width: 50px; height: 50px;" alt="selected items">';
            itemDetailsHtml += '</div>';
            itemDetailsHtml += '<div class="selected-item-amt">';
            itemDetailsHtml += '<h5>' + item.product_title + '</h5>';
            itemDetailsHtml += '<h5>&#8358; ' + item.product_price.toFixed(2) + '</h5>';
            itemDetailsHtml += '</div>';
            itemDetailsHtml += '<div class="remove-item">';
            itemDetailsHtml += '<button type="button">&times;</button>';
            itemDetailsHtml += '</div>';
            itemDetailsHtml += '</div>';
            totalPrice += item.product_price * item.product_qunatity;
         });
         totalAmtHtml = '<h2> Total: &#8358; <span>' + totalPrice.toFixed(2) + '</span></h2>';
         $('#asideBarTotalAmt').html(totalAmtHtml);
         $('#asideBarItemDetails').html(itemDetailsHtml);
       }

     });  
