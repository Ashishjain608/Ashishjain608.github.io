/* Google Analytics (GA4) for everything served on qriousguy.com.
 *
 * One file, one property. Site pages load it from components.head(); a project
 * page under qriousguy.com/<repo>/ gets the same tracking with one line:
 *     <script src="/analytics.js" async></script>
 *
 * GA4 Enhanced Measurement already records page views, scroll depth, outbound
 * clicks and traffic source. This adds what it misses:
 *   file_download  a click on a .dmg/.pkg/.zip/.pdf/... link (GA4 ignores .dmg)
 *   contact        a click on a mailto: link
 *
 * Only runs on qriousguy.com, so local previews don't pollute the numbers.
 * Add ?ga_debug=1 to any URL to force it on and see hits in GA DebugView.
 */
(function () {
  'use strict';

  var ID = 'G-VEELEGZECG';
  var debug = /[?&]ga_debug\b/.test(location.search);
  if (location.hostname !== 'qriousguy.com' && !debug) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('js', new Date());
  gtag('config', ID, debug ? { debug_mode: true } : {});

  var loader = document.createElement('script');
  loader.async = true;
  loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
  document.head.appendChild(loader);

  var DOWNLOAD = /\/([^\/?#]+\.(dmg|pkg|zip|pdf|exe|msi|appimage|deb))(?:[?#]|$)/i;

  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    var href = link.href;
    var text = (link.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100);

    if (/^mailto:/i.test(href)) {
      gtag('event', 'contact', { method: 'email' });   // GA redacts the address anyway
      return;
    }
    var file = href.match(DOWNLOAD);
    if (file) {
      gtag('event', 'file_download', {
        file_name: file[1],
        file_extension: file[2].toLowerCase(),
        link_url: href,
        link_text: text
      });
    }
  }, true);
})();
