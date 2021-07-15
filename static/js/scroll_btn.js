// Hide/show scroll btn
$(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
        $('.scroll-btn').removeClass('hide');
    } else {
        $('.scroll-btn').addClass('hide');
    }
});

$('.scroll-btn').click(function () {
    window.scrollTo(0, 0);
});