$(function(){

	var newVal = 0;

	$(document).on('click', '.number-spinner button', function () {    
		var btn = $(this),
		oldValue = btn.closest('.number-spinner').find('input').val().trim();
		
		if (btn.attr('data-dir') == 'up') {
			newVal = parseInt(oldValue) + 1;
		} else {

			if (oldValue > 0) {
				newVal = parseInt(oldValue) - 1;
			} else {
				newVal = 0;
			}
		}
		btn.closest('.number-spinner').find('input').val(newVal);
	});

	$(document).on('click', '.submit button', function () {   
		var text = document.getElementById("errnotes").value; 
		d = 'num_err='+newVal+'&err_descrip='+text;
		// console.log(d);
		// console.log(text);
		$.ajax({
			url: '/submission',
			data: d,
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});