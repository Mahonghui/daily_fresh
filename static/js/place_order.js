

$('#order_btn').click(function() {

        address_id = $('input[name="address_id"]').val()
        pay_method = $('input[name="pay_style"]').filter(':checked').val()
        sku_ids = $(this).attr('sku_ids')
        csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
        context = {
            'address_id': address_id,
            'pay_method': pay_method,
            'sku_ids': sku_ids,
            'csrfmiddlewaretoken':csrf_token
            }


        $.post('/order/commit', context, function(data){
            if(data.status == 1)
            {
                alert(data.msg)
                setTimeout(function(){
                     window.location.href = '/users/user_center_order/1'
                }, 1000)

            }
            else
            {
                alert(data.errmsg)
            }
        })
        localStorage.setItem('order_finish',2);

        $('.popup_con').fadeIn('fast', function() {

            setTimeout(function(){
                $('.popup_con').fadeOut('fast',function(){
                    window.location.href = 'index.html';
                });
            },3000)

        });
    });