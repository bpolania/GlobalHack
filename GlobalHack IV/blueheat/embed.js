;(function(window, undefined) {
  function translateSourceUrl(el, container) {
    var pathname = el.pathname[0] === '/' ? el.pathname : '/' + el.pathname;
    var isIE = false;
    /*@cc_on isIE = @_jscript_version;@*/
    var forceHttps = isIE === 9 && el.hostname === 'lockerdome.com';

    var protocol = forceHttps ? 'https:' : window.location.protocol;
    var args = 'pubid=' + encodeURIComponent(el.id) + '&pubo=' + encodeURIComponent(window.location.protocol + '//' + window.location.host) + '&width=' + Math.min(1000, container.offsetWidth);
    var search = el.search ? el.search + '&' + args : '?' + args;
    var origin = protocol + '//' + el.hostname;
    // Only add a port number if it could not be implied.
    var port = forceHttps ? 443 : parseInt(el.port, 10);
    if (port && !((protocol === 'https:' && port === 443) || (protocol === 'http:' && port === 80))) {
      origin += ':' + port;
    }
    return {
      url: origin + '/embed' + pathname + search + el.hash,
      host: el.host,
      origin: origin,
      id: el.id,
      el: el
    };
  }
  var eventProp = document.addEventListener ? 'addEventListener' : 'attachEvent';
  var eventName = document.addEventListener ? 'message' : 'onmessage';

  var idMap = {};

  function renderWidget(id) {
    try {
      var el_hide = document.getElementById(id + '-equiv');
      if (el_hide) el_hide.style.display = 'none';
    } catch(e) {}
    var el = document.getElementById(id);
    if (!el) return;
    var container = document.createElement("div");
    container.style.display = 'block';
    el.parentNode.replaceChild(container, el);

    if (configureIframe()) return;

    var interval = setInterval(function() {
      if (configureIframe()) {
        clearInterval(interval);
      }
    }, 100);

    function configureIframe() {
      if (!container.offsetWidth) return false;

      var info = translateSourceUrl(el, container);
      var iframe = document.createElement('iframe');
      iframe.setAttribute('src', info.url);
      var dataWidth = el.getAttribute('data-width');
      var dataExtraCssText = el.getAttribute('data-iframe-extra-csstext') || '';
      iframe.setAttribute('width', dataWidth ? dataWidth : '100%');
      iframe.setAttribute('scrolling', 'no');
      iframe.setAttribute('frameBorder', '0');
      iframe.setAttribute('seamless', '');
      iframe.style.cssText = '-webkit-box-sizing: border-box !important; -moz-box-sizing: border-box !important; box-sizing: border-box !important; border-radius: 4px; max-width: 1000px; min-width: 225px; border: 0px solid #dedede;' + dataExtraCssText;
      info.frame = iframe;
      info.container = container;
      container.appendChild(iframe);
      info.contentWindow = iframe.contentWindow;
      idMap[el.id] = info;

      return true;
    }
  }

  window[eventProp](eventName, handleEvent);
  function handleEvent(event) {
    try {
      var data = JSON.parse(event.data);
      var info = idMap[data && data.id];
      if (!info || event.origin !== info.origin) return;
      if (data.type === 'height') {
        info.frame.setAttribute('height', data.value);
        info.frame.style.height = data.value + 'px';
      } else if (data.type === 'width') {
        info.frame.setAttribute('width', data.value);
      }
    } catch (e) {

    }
  }

  var ld_ids = window.ldInit;
  function renderAllWidgets() {
    var ld = ld_ids;
    if (!ld || !ld.length) return;
    var els = [];
    for (var i = 0, len = ld.length; i < len; ++i) renderWidget(ld[i]);
  }
  setTimeout(renderAllWidgets, 0);
  window.ldInit = { push: renderWidget };
})(this);
