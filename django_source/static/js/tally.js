!function ($) {
  $(function(){
    var $window = $(window)

    // side bar
    $('.tally-sidenav').affix({
      offset: {
        top: function () { return $window.width() <= 980 ? 60 : 0 }
      , bottom: 270
      }
    })
  })
}(window.jQuery)