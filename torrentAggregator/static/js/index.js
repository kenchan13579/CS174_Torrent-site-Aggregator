$(document).ready(function (){
    var spinnerShowed = false;
    $("form#index").submit( function(e){
        if ( !spinnerShowed){
            e.preventDefault();
            $(".spinner-mask").css("display","block");
            spinnerShowed = true;
            setTimeout(function(){
                $("#index").submit();
            },100);
        }

    });
});
