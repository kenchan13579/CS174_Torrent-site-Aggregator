function init(item_per_page) {
	var $items = $(".pagination-item");
	var number_of_items = $items.length;
	var number_of_pages = Math.round(number_of_items / item_per_page);
	if (number_of_pages <= 1) {
		return true;
	}
	$("#pagination-ctrl")
		.append("<button id='prevPage' class='btn btn-success'><i class='fa fa-chevron-circle-left'></i></button><button id='nextPage' class='btn btn-success'><i class='fa fa-chevron-circle-right'></i></button>");
	$items.hide();
	$items.slice(0, item_per_page).show();
	var current_page = item_per_page;
	$("#prevPage").click(prevPage);
	$("#nextPage").click(nextPage);

	function nextPage() {

		if (current_page + item_per_page <= number_of_items) {
			$items.hide();
			$items.slice(current_page, increment(current_page)).show();
		} else if (current_page + item_per_page > number_of_items && current_page < number_of_items) {
			$items.hide();
			$items.slice(current_page, number_of_items).show();
			current_page += item_per_page;
		}

	}

	function prevPage() {

		if (current_page > item_per_page) {
			$items.hide();
			current_page -= item_per_page;
			$items.slice(current_page - item_per_page, current_page).show();
		}
	}

	function increment(num) {
		var result = num + item_per_page;
		current_page += item_per_page;
		return result;
	}



}
init(25);