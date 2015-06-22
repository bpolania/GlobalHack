window.LD = (function() {
  var queryParams = decodeURIComponent(window.location.href.split('?').slice(1).join('?'));
  if (queryParams[queryParams.length - 1] === '#')
    queryParams = queryParams.substring(0, queryParams.length - 1);
  var LD = JSON.parse(queryParams || '{}');

  window.addEventListener("message", receiveMessage, false);

  function receiveMessage(raw_event) {
    if (raw_event.origin !== LD.ld_url) {
      console.log('Ignoring post message from non-lockerdome domain ', raw_event.origin);
      return;
    }

    var event = JSON.parse(raw_event.data);
    var event_name = event.name;
    var event_args = event.args;
    if (event_name) {
      var handlers = events[event_name];
      for (var i = 0; i !== handlers.length; ++i) {
        handlers[i].apply(undefined, event.args);
      }
    }
  }

  var events = {
    request_login: [

      function(account_id) {
        LD.account_id = account_id;
      }
    ],
    request_logout: [

      function() {
        LD.account_id = null;
      }
    ]
  };

  LD.on = function(eventName, eventHandler) {
    if (events[eventName]) {
      events[eventName].push(eventHandler);
    } else {
      events[eventName] = [eventHandler];
    }
  };

  LD.request_width = function(new_width) {
    window.parent.postMessage(JSON.stringify({
      name: 'request_width',
      args: [new_width]
    }), '*');
  };

  LD.request_height = function(new_height) {
    window.parent.postMessage(JSON.stringify({
      name: 'request_height',
      args: [new_height]
    }), '*');
  };

  LD.request_redirect = function(path) {
    window.parent.postMessage(JSON.stringify({
      name: 'request_redirect',
      args: [path]
    }), '*');
  };

  return LD;
})();