$(document).ready(function() {
	$(document).on("click", ".icon-url-shortener", function(e) {
		var longLink = $(this).siblings("a").attr("href");
		var dis = $(this);
		// otain the shorten url from google api
		var request = $.ajax({
			url: "https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBkmyfvQ1Tr3p9Ej7qGLySAtzDdyhJwf2w",
			method: "post",
			contentType: "application/json",
			data: JSON.stringify({"longUrl": longLink})
		});
		request.done(function(data) {
			if (data["id"] && data["id"].length > 0) {
				var shortenURL = data["id"];
				dis.attr("data-clipboard-text" , shortenURL);
				// copy this link to clipboard
				var clip = new ZeroClipboard(dis);
				
				dis.html("&#10004 Copied to cliboard");
				setTimeout(function(){
					dis.html("Share it");
				},5000);
			}
		});
		request.fail(function(data) {
			console.error(data);
		});



	});
});