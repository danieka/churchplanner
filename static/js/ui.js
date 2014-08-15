function menus() {
    $( ".menu_launcher").button();
    $( ".menu_launcher").css('width', '11em');
    $( ".menu_container").css('width', '11em');

    $(".menu_launcher").mouseenter(function() {

        // .position() uses position relative to the offset parent, 
        var pos = $(this).position();

        // .outerWidth() takes into account border and padding.
        var width = $(this).outerWidth();
        
        //show the menu directly over the placeholder
        $(this).find(".menu_container").css({
            position: "absolute",
            top: (pos.bottom - 101) + "px",
            left: (pos.left + width) + "px"
            }).show();
            
            $(this).find(".menu_container").position({
            of: $(this),
            my: "left top",
            at: "left bottom",
            collision: "none"});
    });
    
    $(".menu_container").mouseleave(function() {
        $(this).hide();         
    });
    
    $(".menu_launcher").mouseleave(function() {
        $(this).find(".menu_container").hide();         
    });
}

