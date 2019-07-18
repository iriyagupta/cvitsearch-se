(function( $ ){
  $( function(){
    $(".enlarge.inline-demo").data("options", {
      button: true,
      hoverZoomWithoutClick: true,
      delay: 300,
      flyout: {
        width: 100,
        height: 100
      },
      placement: "inline",
      magnification: 2
    });


    $( document ).bind( "enhance", function(){
      $( "body" ).addClass( "enhanced" );
    });

    $( document ).trigger( "enhance" );
  });
}( jQuery ));
