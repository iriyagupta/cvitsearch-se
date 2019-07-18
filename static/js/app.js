// Initialize Foundation framework
// $(document).foundation();

// Push footer to bottom of page
// function pushFooter() {
//     var footer = $("#footer");
//     var pos = footer.position();
//     var height = $(window).height();
//     height = height - pos.top;
//     height = height - footer.height();
//     if (height > 0) {
//         footer.css({
//             'margin-top': height + 'px'
//         });
//     }
// }
// $(window).bind("load", pushFooter());

// Scroll to top
// jQuery(document).ready(function() {
//     var offset = 220;
//     var duration = 500;
//     jQuery(window).scroll(function() {
//         if (jQuery(this).scrollTop() > offset) {
//             jQuery('.back-to-top').fadeIn(duration);
//         } else {
//             jQuery('.back-to-top').fadeOut(duration);
//         }
//     });

//     jQuery('.back-to-top').click(function(event) {
//         event.preventDefault();
//         jQuery('html, body').animate({scrollTop: 0}, duration);
//         return false;
//     });
// });

function flashNoty(type, message) {
    if (type === 'info') {
       type = 'information';
    }
    new Noty({
        text: message,
        type: type,
        layout: 'topRight',
        timeout: 5000,
        progressBar: true,
        closeWith: ['click'],
        theme: 'relax',
        dismissQueue: true,
        maxVisible: 5,
        animation: {
            open: 'animated fadeInRightBig',
            close: 'animated fadeOutRightBig',
            easing: 'swing',
            speed: 500
        },
    }).show();
}

$(function () {
  $('[data-toggle="popover"]').popover({
    container: '.popover-container',
    content: $('#popoverContent').html(),
    html: true,
    placement: 'bottom',
    trigger: 'hover',
})
});

$('.dropdown-menu a.dropdown-toggle').on('click', function(e) {
  if (!$(this).next().hasClass('show')) {
    $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
  }
  var $subMenu = $(this).next(".dropdown-menu");
  $subMenu.toggleClass('show');


  $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
    $('.dropdown-submenu .show').removeClass("show");
  });


  return false;
});