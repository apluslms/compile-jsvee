/* JSVEE animations */
(function($) {
  'use strict';

  if (window.JSVEE === undefined) {
    return;
  }

  JSVEE.animations = {};

  /**
   * Returns the requested animation.
   *
   * @param id The unique id of the animation
   * @memberOf JSVEE.animations
   */
  JSVEE.animations.getAnimation = function (id) {

    if (JSVEE.animations.hasOwnProperty(id)) {
      return JSVEE.animations[id];
    }

    return null;

  };

  @@ANIMATIONS@@

  /* Load all animations */
  $(document).on('aplus:translation-ready', function () {
    $('.jsvee-animation, .animation').each(function () {
      $(this).addClass('jsvee-animation');
      var id = $(this).data('id');
      if (id) {
        new JSVEE.ui(id, this);
      }
    });
  });
}(jQuery));
