	function update_price_count()
	{
		total_count = 0
		total_price = 0
		$('.cart_list_td').find(':checked').parents('ul').each(function (){
		count = $(this).find('.num_show').val()
		price = $(this).children('.col07').text()
		total_count += parseInt(count)
		total_price += parseFloat(price)
		})
		$('.settlements').find('em').text(total_price.toFixed(2))
		$('.settlements').find('b').text(total_count)
	}
	function select_all(obj)
	{
		$('.cart_list_td').find(':checkbox').each(function(){
		$(this).prop('checked', obj.checked)
		})
		update_price_count()
	}
    function update_good_sum(ul)
	{
		count = parseInt(ul.find('.num_show').val())
		price = parseFloat(ul.children('.col05').text())

		good_sum = count*price
		ul.children('.col07').text(good_sum.toFixed(2) + '元')
	}

	$('.cart_list_td').find(':checkbox').change(function(){
		len = $('.cart_list_td').find(':checkbox').length
		checked_len = $('.cart_list_td').find(':checked').length

		if(checked_len < len)
		{
			$('.settlements').find(':checkbox').prop('checked', false)
		}
		else
		{
			$('.settlements').find(':checkbox').prop('checked', true)
		}

		update_price_count()
	})


	$('.add').click(function(){

		sku_id = $(this).next().attr('sku_id')
		count = parseInt($(this).next().val())
		count+=1

		csrf_token = $('input[name="csrfmiddlewaretoken"]').val()

		params = {	'sku_id': sku_id,
					'amount': count,
					'csrfmiddlewaretoken': csrf_token
				}

		$.ajaxSettings.async = false
		update_err = true
		total = 0
		$.post('/cart/update', params, function(data){
			if(data.status == 1)
			{
			    total = data.sum
				update_err = false

			}
			else
			{
                alert(data.errmsg)
			}

		})

		$.ajaxSettings.async = true

		if(update_err == false)
		{
			$(this).next().val(count)
			update_good_sum($(this).parents('ul'))
			is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
			if(is_checked)
				update_price_count()
		}
		$('.total_count').children('em').text(total)
	})


	$('.minus').click(function(){

		sku_id = $(this).prev().attr('sku_id')
		count = parseInt($(this).prev().val())
		count-=1
		if(count <=0 )
			count = 1
		csrf_token = $('input[name="csrfmiddlewaretoken"]').val()

		params = {	'sku_id': sku_id,
					'amount': count,
					'csrfmiddlewaretoken': csrf_token
				}

		$.ajaxSettings.async = false
		update_err = true
		total = 0
		$.post('/cart/update', params, function(data){
			if(data.status == 1)
			{
			    total = data.sum
				update_err = false

			}
			else
			{
				alert(data.errmsg)
			}

		})

		$.ajaxSettings.async = true

		if(update_err == false)
		{
			$(this).prev().val(count)
			update_good_sum($(this).parents('ul'))
			is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
			if(is_checked)
				update_price_count()
		}
		$('.total_count').children('em').text(total)

	})

	$('.num_show').blur(function(){
	    count = parseInt($(this).val())
	    sku_id = $(this).attr('sku_id')
	    if(isNaN(count) || count <=0)
	        alert('请输入合法数值')
	        $(this).val(1)
	    csrf_token = $('input[name="csrfmiddlewaretoken"]').val()

	    params = {
	        'sku_id': sku_id,
	        'amount': count,
	        'csrfmiddlewaretoken': csrf_token
	    }

	    $.ajaxSettings.async = false
	    total = 0
	    update_err = true
	    $.post('/cart/update', params, function(data){
	        if( data.status == 1 )
	            {
	                update_err = false
	                total = data.sum
	            }
	         else
	            alert(data.errmsg)

	    })

	    $.ajaxSettings.async = true

	    if(update_err == false)
		{
			$(this).val(count)
			update_good_sum($(this).parents('ul'))
			is_checked = $(this).parents('ul').find(':checkbox').prop('checked')
			if(is_checked)
				update_price_count()
		}
		$('.total_count').children('em').text(total)
	})

	$('.cart_list_td').children('.col08').children('a').click(function(){

	    sku_id = $(this).parents('ul').find('.num_show').attr('sku_id')
	    csrf_token = $('input[name="csrfmiddlewaretoken"]').val()

        params = {
            'sku_id': sku_id,
            'csrfmiddlewaretoken': csrf_token
        }
        current_url = $(this).parents('ul')
	    $.post('/cart/delete', params, function(data){
	        if(data.status == 1){
	            // 删除成功
                current_url.remove()
                update_price_count()
                // empty() 只移除子元素，不删除自己
//                is_checked = current_url.find(':checkbox').prop('checked')
//                if(is_checked)
//                    update_price_count()
                $('.total_count').children('em').text(data.sum)
	        }
	        else{
                alert(data.errmsg)
	        }

	    })
	})

