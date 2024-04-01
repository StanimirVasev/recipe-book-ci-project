/*
    jQuery for MaterializeCSS initialization
*/

$(document).ready(function () {
    $(".sidenav").sidenav({edge: "right"});
    $('.slider').slider({
        indicators: false
      });
    $('.collapsible').collapsible();
    $("select").formSelect();
});