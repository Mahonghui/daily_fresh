	update_total_price()

		function update_total_price()
		{
			price = $('.show_price').children('em').text()
			amount = $('.num_show').val()

			price = parseFloat(price)
			amount = parseInt(amount)

			total_price = price * amount

			$('.total').children('em').text(total_price.toFixed(2) + '元')
		}

		function change_amount(obj)
		{
			class_name = obj.getAttribute('class')
			amount = parseInt($('.num_show').val())
			if(class_name == 'add fr')
			{
				amount++
				$('.num_show').val(amount)

			}

			if(class_name == 'minus fr')
			{
				if(amount > 1)
				{
					amount--
					$('.num_show').val(amount)
				}
			}
			update_total_price()
		}

		function vali_amount(input)
		{
			amount = input.value
			if(isNaN(amount) || amount.trim().length == 0 || parseInt(amount) <=0 )
				amount = 1
			input.value = parseInt(amount)
			update_total_price()
		}



		var $add_x = $('#add_cart').offset().top;
		var $add_y = $('#add_cart').offset().left;

		var $to_x = $('#show_count').offset().top;
		var $to_y = $('#show_count').offset().left;


		$('#add_cart').click(function(){
			sku_id = $(this).attr('sku_id')
			amount = $('.num_show').val()
			csrf_token = $('input[name="csrfmiddlewaretoken"]').val()

			params = {'sku_id': sku_id,
						'amount': amount,
					'csrfmiddlewaretoken': csrf_token
				}

		$.post('/cart/add', params, function(data)
		{
			if(data.status == 1){
				// 添加成功
				$(".add_jump").css({'left':$add_y+80,'top':$add_x+10,'display':'block'})

				$(".add_jump").stop().animate
					({
						'left': $to_y+7,
						'top': $to_x+7},
						"fast", function() {
							$(".add_jump").fadeOut('fast',function()
								{
									$('#show_count').html(data.total_count);
								}
							);
					});
			}
			else{
				alert(data.errmsg)
			}
		})
	})