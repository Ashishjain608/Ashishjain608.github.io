/* Page behaviour. Four small things, no dependencies:
 *   reveals        sections fade and rise once, as they enter the viewport
 *   scroll hint    appears 1000ms after load, leaves on the first scroll
 *   portrait       settles from 1.05 to 1.0 over the first screen
 *   nav state      marks which chapter you are currently inside
 * Everything degrades to "visible and static" under prefers-reduced-motion.
 */
(function () {
  'use strict';

  var reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));

  /* --- scroll reveals, fire once (monks) ------------------------------- */
  // Children are indexed so CSS can stagger them off a single --i custom property.
  reveals.forEach(function (section) {
    var children = section.querySelectorAll('.body > *, .linkrow > a');
    for (var i = 0; i < children.length; i++) {
      children[i].style.setProperty('--i', i);
    }
  });

  if (reducedMotion || !('IntersectionObserver' in window)) {
    reveals.forEach(function (section) { section.classList.add('in'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (section) { observer.observe(section); });
  }

  /* --- scroll hint, 1000ms after load (measured off monks.com) --------- */
  var hint = document.getElementById('hint');
  if (hint) {
    setTimeout(function () { hint.classList.add('visible'); }, 1000);
    addEventListener('scroll', function () {
      if (scrollY > 80) hint.classList.remove('visible');
    }, { passive: true });
  }

  /* --- portrait settle + which chapter you are in ---------------------- */
  var portrait = document.querySelector('.hero .photo img');
  var jumps = Array.prototype.slice.call(document.querySelectorAll('.nav-group.chapters a'));
  var sections = jumps.map(function (link) {
    var id = link.getAttribute('href').split('#')[1];
    return id ? document.getElementById(id) : null;
  });
  var pending = false;

  function onScroll() {
    pending = false;

    if (portrait && !reducedMotion) {
      var progress = Math.min(1, scrollY / innerHeight);
      portrait.style.transform = 'scale(' + (1.05 - 0.05 * progress).toFixed(4) + ')';
    }

    var line = scrollY + innerHeight * 0.35;
    var current = -1;
    sections.forEach(function (section, i) {
      if (section && section.offsetTop <= line) current = i;
    });
    jumps.forEach(function (link, i) { link.classList.toggle('active', i === current); });
  }

  addEventListener('scroll', function () {
    if (pending) return;
    pending = true;
    requestAnimationFrame(onScroll);
  }, { passive: true });

  onScroll();
})();
