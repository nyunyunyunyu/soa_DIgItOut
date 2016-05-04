function load_script(url) {
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = url;
    var x = document.getElementsByTagName('head')[0];
    x.appendChild(s);
}

jQuery(document).ready(function($) {
   "use strict";
   
    // FOR CART ONLY
    if ($('.woocommerce-cart').length > 0){
      //add to cart
      $('.checkout-button').click(function(){
         ga('send', 'event', 'cart', 'checkout');
      });
    }
   
    // FOR CHECKOUT
    if ($('.woocommerce-checkout').length > 0){
      //add to cart
      $('#place_order').click(function(){
         ga('send', 'event', 'checkout', 'proceed');
      });
    }
   
    // THANK YOU PAGE
    if ($('.thanksforpurchase').length > 0){
      //visited
      ga('send', 'event', 'thankyou-page', 'purchase');
    }

    $("body").click(function() {
        $(".top-menu").parent().removeClass("active");
    });

    $(".top-menu").click(function(e) {
        e.stopPropagation();
    });

    $(".top-menu").click(function() {
        $(parent).toggleClass("active");
    });
    console.log("in click");
    // SEARCH
    $('.gobutton').click(function() {
        $('#search').submit();
    });

    $(document).click(function() {
        $(".top-menu.search").removeClass('selected');
    });

    $(".top-menu.search").click(function(event) {
        $(this).addClass('selected');
        $('.search-input').focus();
        event.stopPropagation();
    });

    // CONTACT FORM
    $(document).on('submit', '#dm_contact_form_1', function() {
        var form_container = $(this);
        $('#dm_contact_form #message').empty();
        $('#submit', form_container).attr('disabled', 'disabled');
        $('.loader', form_container).show();

        $.ajax({
            type: 'post',
            url: '/wp-admin/admin-ajax.php',
            data: form_container.serialize() + '&action=dm_contact',
            success: function(response) {
                $('#dm_contact_form #message').html(response).slideDown();

                if (response.match('success') != null) {
                    form_container.slideUp();
                }

                $('.loader', form_container).hide();
                $('#submit', form_container).removeAttr('disabled');
            }
        });

        return false;
    });

    // CONTACT FORM ON CHANGE SUBJECT
    var contact_form_array = [
        'startup-support',
        'startup-wordpress-support',
        'flat-ui-support',
        'qards-support',
        'slides-support'
    ];

    if($('#dm_contact_form_1').length > 0 && $.inArray($('#dm_contact_form_1 #subject').val(), contact_form_array) !== -1) {
        $('#dm_contact_form_1 #order_number').closest('div').show();
    }

    $('#dm_contact_form_1').on('change', '#subject', function() {
        if($.inArray($(this).val(), contact_form_array) !== -1) {
            $('#dm_contact_form_1 #order_number').closest('div').show();
        } else {
            $('#dm_contact_form_1 #order_number').closest('div').hide();
        }
    });

    // LOAD ASYNC
    load_script('//platform.twitter.com/widgets.js');
    load_script('//apis.google.com/js/plusone.js');
    load_script('//connect.facebook.net/en_US/sdk.js#xfbml=1&appId=368289576549864&version=v2.0');
});
