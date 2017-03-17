/*************************************************************************
 *
 * WEEMO INC.
 *
 *  Rtcc.js - v @@version.@@release
 *  [2013] Weemo Inc.
 *  All Rights Reserved.
 *
 * NOTICE:  All information contained herein is, and remains
 * the property of Weemo Inc.
 * The intellectual and technical concepts contained
 * herein are proprietary to Weemo Inc.
 * Dissemination of this information or reproduction of this material
 * is strictly forbidden unless prior written permission is obtained
 * from Weemo Inc.
 */

/*jslint browser: true*/
/*jslint bitwise: true*/
/*jslint evil: true*/
/*jslint eqeq: true*/
/*global console:true */
/*global XDomainRequest:true */
/*global XMLHttpRequest:true */
/*global alert:true */
/*global MozWebSocket:true */
/*global WebSocket:true*/
/*global DOMParser:true*/
/*global ActiveXObject:true*/
/*global confirm:true*/
/*global JsSIP:true*/
// Utils



(function(window) {

  //http://stackoverflow.com/questions/17618791/noticing-an-odd-difference-between-different-implementations-of-json-stringify
  delete Array.prototype.toJSON; //Prototypejs BUG workaround
  /*! <%= pkg.name %> - v<%= pkg.version %> - <%= grunt.template.today("yyyy-mm-dd") %> 
 Private Injections */
var instance = 0;
/**
* @class The API for the Rtcc service.
* @version @@version.@@release
*
* @author Nicholas Stock, Raphael Boucher.
* @constructor
* @param {string} appId - Value of the web application identifier
* @param {string} token - Token value to authenticate the session on the Rtcc Cloud.<br />If rtccUserType = 'external'[1], enter the UID of the 'internal' user. <br />[1]: The 'internal' user associated with the UID must be authenticated before connecting the external user.
* @param {string} rtccUserType - This variable describes the type of user, it must be one of the following:<br />
    <br />
      <table  class="fieldtable">
        <tbody>
          <tr>
            <td>internal</td>
            <td>For authenticated users</td>
          </tr>
          <tr>
            <td>external</td>
            <td>For user not authenticated in the web app</td>
          </tr>
        </tbody>
      </table>
      <br />
      More information about the rtccUserType <a href="https://github.com/weemo/Rtcc.js/blob/master/docs/start.md#weemo-type">here</a>

* @param {object} [options] - Value of several options => options.container : id => id of your own html element where "rtcc video box" is displayed. (only in webRTC)
* @param {string} [options.debugLevel]
* <table class="fieldtable">
* <thead><th>Value</th><th>Description</th></thead>
* <tr><td>0</td><td>No debug messages</td></tr>
* <tr><td>1</td><td>First level of debug messages</td></tr>
* <tr><td>3</td><td>Detailed debug messages</td></tr>
* </table>
* @param {string} [options.displayName] - Value of the display name.
	     * Must respect naming rules:
					<ul>
					<li>String – max 127 characters</li>
					<li>Not Null</li>
					<li>UTF-8 Characters except: ", ,' (single quote, double quote, space)</li>
					<li>Case sensitive</li>
					</ul>
* @param {bool}  [options.defaultStyle] - This property is used when connecting using WebRTC.<br />
                                        False if you don't want to load the default stylesheet and use your own.
                                        <br />
                                        Defaults to true.
* @param {string} [options.container] - An HTML element id, in which the video box is integrated. If used, this feature automatically disables drag&drop for the video box.
* @param {string} [options.uiUrl] - A URL for your own implementation of the UI.
* @param {string} [options.uiCssUrl] - A URL for a custom CSS file.
* @param {string } [options.mode_parameter] - Mode used by application. can be `plugin_webrtc` or `webrtc_only` or `plugin_only`
* @param {string } [options.uiVersion] - 3 digit ui version. example: `1.3.3`
* @param {string|bool} [options.uiDialToneUrl] - A URL for a custom dial tone. If set to false, no dial tone will be used.
* @param {string|bool} [options.uiRingToneUrl] - A URL for a custom ring tone. If set to false, no ring tone will be used.
* @param {bool} [options.standAlone] - if true, connect to rtcc cloud, but do not register to sip server - calls will not be possible. Used for mobile
*
* @return {Rtcc} A Rtcc object
*/
var Rtcc = function() {
  instance++;
  var modeMap = {
    'wd_webrtc': 'driver_webrtc',
    'wd_only': 'driver_only',
    'plugin_webrtc': 'plugin_webrtc',
    'plugin_only': 'plugin_only',
    'webrtc_only': 'webrtc_only'
  }

  // Set browser vars
  var mode = "@@MODE@@",
    downloadUrl = '@@DOWNLOAD_URL@@',
    global_config,
    version = "@@version.@@release",
    endpointUrl = "",
    actions = {};

  /*! <%= pkg.name %> - v<%= pkg.version %> - <%= grunt.template.today("yyyy-mm-dd") %> 
 Private Injections */
actions.authenticate = function() {
  var rtccUserType = global_config.rtccUserType;
  var endpointUrl = global_config.endpointUrl;
  var force = globalVars.force_connect;
  if (rtccUserType === "internal" || rtccUserType === "external" || rtccUserType === "digit_external") {
    if (endpointUrl !== "" && rtccUserType === "internal") {
      var xmlhttp = new_ajax_request();
      var that = this;
      xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
          var data = JSON.parse(xmlhttp.responseText);
          //TODO to be confirmed
          globalVars.token = data.token;
          weemo.requests.run('verify_user');
          run_client_callback(weemo, 'onConnectionHandler', ["connectedCloud", 0]);
          apiEvents.trigger('cloud.connect');
        }
        if (xmlhttp.readyState === 4 && xmlhttp.status === 500) {
          json = JSON.parse(xmlhttp.responseText);
          var error = json.error || json.error_description;
          if (error) {
            run_client_callback(weemo, 'onConnectionHandler', ["rtccAuthApiError", error]);
            apiEvents.trigger('cloud.authenticate.error', error);
          }
        }
      };
      xmlhttp.open("GET", endpointUrl, true);
      xmlhttp.setRequestHeader("Cache-Control", "no-cache");
      xmlhttp.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2005 00:00:00 GMT");
      xmlhttp.send();
    } else {
      weemo.requests.run('verify_user');
      run_client_callback(weemo, 'onConnectionHandler', ["connectedCloud", 0]);
      apiEvents.trigger('cloud.connect');
    }

  } else {
    run_client_callback(weemo, 'onConnectionHandler', ["rtccUserTypeNotExist", 0]);
    apiEvents.trigger('cloud.authenticate.error', 'User type ' + rtccUserType + ' does not exists.');
  }
};

actions.turnProbing = function(probingSuccess, probingFailure, bypassTurnProbeTest) {
  if (bypassTurnProbeTest) {
    return probingSuccess();
  }
  var success = false;
  var peer_connection;
  var msg;
  var failed_timeout = global_config.turn_probing_timeout;
  var timeout_id = false;

  function defaultErrorHandling(err) {
    debug(err);
  }

  function setLocalDescriptionCallbackProbing() {}

  function onLocalDescriptionProbing(description) {
    timeout_id = setTimeout(function() {
      run_client_callback(weemo, 'onConnectionHandler', ["unableToReachTurnServer", 0]);
      apiEvents.trigger('cloud.turn.error', 'Unable to reach TURN server.');
      probingFailure();
    }, failed_timeout);

    peer_connection.setLocalDescription(description, setLocalDescriptionCallbackProbing, defaultErrorHandling);
  }

  function onIceCandidateProbing(event) {
    if (event.candidate) {
      if (!success && event.candidate.candidate.search("typ relay") != -1) {
        success = true;
        clearTimeout(timeout_id);
        peer_connection.close();
        run_client_callback(weemo, 'onConnectionHandler', ["turnProbeOk", 0]);
        apiEvents.trigger('cloud.turn.ok');
        probingSuccess();
      }
    }
  }

  function startTurnProbing() {
    success = false;
    var pcConfig = getPeerConnectionConfig(webrtcFacade.turn);

    peer_connection = new RTCPeerConnection(pcConfig);
    peer_connection.onicecandidate = onIceCandidateProbing;

    var constraint = {
      mandatory: {
        OfferToReceiveAudio: true,
        OfferToReceiveVideo: true
      }
    };

    peer_connection.createOffer(onLocalDescriptionProbing, defaultErrorHandling, constraint);
  }
  startTurnProbing();
};





actions.start_webrtc = function(args) {
  var that = this;
  var connectWebRtc = function(url) {
    vent.once([{
      event: 'facade_proxy_closed',
      action: function() {
        args.on_webrtc_finished('cannot_connect');
      }
    }, {
      event: 'facade_proxy_opened',
      action: function() {
        vent.once({
          event: 'facade_proxy_closed',
          action: function() {
            run_client_callback(weemo, 'onConnectionHandler', ['disconnectedWebRTC', 0]);
            apiEvents.trigger('client.disconnect');
            apiEvents.trigger('cloud.disconnect');
            args.on_webrtc_finished('disconnected');
          }
        });
        webrtcFacade.open();
      }
    }]);
    webrtcFacade.connectWebRTC(url);
  };


  var probes_ok = function(return_data) {
    var handler_data = {
      server: return_data.probe.server,
      name: return_data.probe.name
    };
    run_client_callback(weemo, 'onConnectionHandler', ["probesOk", handler_data]);
    apiEvents.trigger('cloud.realtimeplatform.ok');

    var webrtc = return_data.probe.webrtc;
    //TODO use server to pick web-p
    webrtcFacade.webrtc_server = webrtc;
    webrtcFacade.probe_server = return_data.probe.server;
    webrtcFacade.localAddress = return_data.localAddress;
    webrtcFacade.latency = return_data.probe.latency;
    webrtcFacade.port = return_data.probe.port;
    webrtcFacade.turn = return_data.probe.turn;

    var url = global_config.webpProtocol + '://' + webrtc;
    //var url = 'ws://188.165.163.142:80'; // Qualif
    //var url = 'ws://188.165.163.136:80'; // dev

    actions.turnProbing(function() {
      connectWebRtc(url);
    }, function() {
      if (args.allow_turn_failure === true) {
        connectWebRtc(url);
      } else {
        args.on_webrtc_finished.call(that, 'turn_probing_failed');
      }
    }, args.bypassTurnProbeTest);
  };


  vent.once([{
    event: 'hap_ok',
    action: function(params) {
      vent.once([{
        event: 'probes_ok',
        action: probes_ok
      }, {
        event: 'probes_nok',
        action: function() {
          run_client_callback(weemo, 'onConnectionHandler', ["unableToReachProbes", 0]);
          apiEvents.trigger('cloud.realtimeplatform.error', 'Unable to reach probes');
          args.on_webrtc_finished.call(that, 'cannot_connect_probes');
        }
      }]);
      run_client_callback(weemo, 'onConnectionHandler', ["hapOk", 0]);
      apiEvents.trigger('cloud.haproxy.ok');

      webrtcFacade.choose_realtime_platform(params.hap);
    }
  }, {
    event: 'hap_nok',
    action: function() {
      if (global_config.current_hap === 0) {
        global_config.current_hap = 1;
      } else {
        global_config.current_hap = 0;
      }
      run_client_callback(weemo, 'onConnectionHandler', ['unableToReachHap', 0]);
      apiEvents.trigger('cloud.haproxy.error', 'Unable to reach HA proxy');
      args.on_webrtc_finished('cannot_connect');
    }
  }]);
  webrtcFacade.getHap();
};
;
(function(actions, weemo) {
  var cb_with_init_timeout = function(cb, data) {
    globalVars.timeout.init_timeout_id = setTimeout(function() {
      cb.apply(null, data);
    }, global_config.timeBetweenConnectionAttempts);
  };

  actions.initialize = function(options) {
    run_client_callback(weemo, 'onConnectionHandler', ["webRTCCapabilities", Number(webrtc_compliant())]);
    apiEvents.trigger('webrtc.capability', Number(webrtc_compliant()));
    if (global_config.standAlone) {
      stand_alone();
    } else {
      var mode_parameter = convert_mode_from_context(global_config.mode_parameter, global_config.os, global_config.force_supported_os, global_config.force_chrome_allows_plugin);
      debug("mode:" + mode_parameter);
      if (mode_parameter) {
        modeConnectionFunction[mode_parameter](options);
      }
    }
  };

  var stand_alone = function() {
    actions.start_webrtc({
      bypassTurnProbeTest: true,
      on_webrtc_finished: function(type) {
        if (global_config.standAlone) { // If sip register has not happened.
          cb_with_init_timeout(stand_alone);
        } else { //If sip register has not happened. and driver is the option
          weemo.initialize({
            offer_driver_on_first_failure: true
          })
        }
      }
    });
  };

  var convert_mode_from_context = function(mode_parameter, os, force, force_chrome_allows_plugin) {
    if (mode_parameter === "webrtc_wd") mode_parameter = 'wd_webrtc';
    if (mode_parameter === "webrtc_plugin") mode_parameter = 'plugin_webrtc';

    debug("convert_mode_from_contextmode:" + mode_parameter);
    if (force_chrome_allows_plugin !== true && system_info().browser === "Chrome" && mode_parameter === "plugin_only") {
      apiEvents.trigger('plugin.browser.error');
      return false;
    } else if (force_chrome_allows_plugin !== true && system_info().browser === "Chrome" && mode_parameter === "plugin_webrtc") {
      return "webrtc_only";
    } else if ((mode_parameter === 'wd_webrtc' || mode_parameter === 'plugin_webrtc') && !wd_supports_os(os, force) && !webrtc_compliant()) {
      run_client_callback(weemo, 'onConnectionHandler', ["unsupportedOS", 0]);
      apiEvents.trigger('error.ossupport');
      debug('Mode:' + mode_parameter + 'unsupportedOS');
      return false;
    } else if ((mode_parameter === 'wd_only' || mode_parameter === 'plugin_only') && !wd_supports_os(os, force)) {
      run_client_callback(weemo, 'onConnectionHandler', ["unsupportedOS", 0]);
      apiEvents.trigger('error.ossupport');
      debug('Mode:' + mode_parameter + 'unsupportedOS');
      return false;
    } else if ((mode_parameter === 'webrtc_only') && (!webrtc_compliant())) {
      debug('Mode set to webRTC only, but browser not compatible with webRTC');
      run_client_callback(weemo, 'onConnectionHandler', ["browserCompatibilityError", null]);
      apiEvents.trigger('webrtc.browser.error');
      return false;
    } else if ((mode_parameter === 'wd_webrtc') && !wd_supports_os(os, force)) {
      return 'webrtc_only';
    } else if (mode_parameter === 'wd_webrtc' && !webrtc_compliant()) {
      return 'wd_only';
    } else if (mode_parameter === "plugin_webrtc" && !webrtc_compliant()) {
      return 'plugin_only';
    } else if (!modeConnectionFunction.hasOwnProperty(mode_parameter)) {
      debug('Mode:' + mode_parameter + ' Not recongnized');
      return false;
    }

    return mode_parameter;
  };


  function disconnectedDriverEvents() {
    run_client_callback(weemo, 'onConnectionHandler', ["disconnectedRtccDriver", 0]);
    apiEvents.trigger('client.disconnect');
    apiEvents.trigger('cloud.disconnect');
  }

  var wd_only = (function() {
    var has_called_onRtccDriverNotStarted = false;

    var current_driver_attempt = 1;
    return function(options) {
      options = options || {};


      var local_has_called_onRtccDriverNotStarted;
      if (options.has_called_onRtccDriverNotStarted === undefined) {
        local_has_called_onRtccDriverNotStarted = has_called_onRtccDriverNotStarted;
      } else {
        local_has_called_onRtccDriverNotStarted = options.has_called_onRtccDriverNotStarted;
      }

      var should_offer_driver = function() {
        if (local_has_called_onRtccDriverNotStarted) {
          return false;
        } else {
          return (options.offer_driver_on_first_failure || current_driver_attempt === global_config.connection_attempts_before_not_started_cb)
        }
      }
      var facade_proxy_closed = function() {
        if (!global_config.stop_reconnection_attempts) {
          debug('RTCCdriver re-connection attempt ' + current_driver_attempt);
          if (should_offer_driver()) {
            debug("cannot reachdriver, calling onRtccDriverNotStarted");
            downloadDriver.call(weemo);
            has_called_onRtccDriverNotStarted = true;
          }
          current_driver_attempt++;
          cb_with_init_timeout(wd_only, [options]);

        } else {
          global_config.stop_reconnection_attempts = false;
        }
      };

      var facade_proxy_opened = function() {
        current_driver_attempt = 1;
        vent.once({
          event: 'facade_proxy_closed',
          action: function() {
            globalVars.state = Rtcc.STATES.NOT_CONNECTED_TO_FACADE;
            disconnectedDriverEvents();
            cb_with_init_timeout(wd_only, [options]);
          }
        });
        driverFacade.open();
      };

      vent.once([{
        event: 'facade_proxy_opened',
        action: facade_proxy_opened
      }, {
        event: 'facade_proxy_closed',
        action: facade_proxy_closed
      }]);
      driverFacade.connect();
    };
  })();

  var installPluginCallbackFired = false;
  var plugin_only = function() {
    var facade_proxy_closed = function() {
      if (!installPluginCallbackFired) {
        downloadPlugin.call(weemo);
        installPluginCallbackFired = true;
      }
      pluginReconnect();
    };

    function pluginReconnect() {
      clearTimeout(globalVars.timeout.pluginConnect);
      globalVars.state = Rtcc.STATES.NOT_CONNECTED_TO_FACADE;
      cb_with_init_timeout(plugin_only);
    }

    var facade_proxy_opened = function() {
      vent.once({
        event: 'facade_proxy_closed',
        action: function() {
          disconnectedDriverEvents();
          pluginReconnect();
        }
      });
      pluginFacade.open();
    };

    vent.once([{
      event: 'facade_proxy_opened',
      action: facade_proxy_opened
    }, {
      event: 'facade_proxy_closed',
      action: facade_proxy_closed
    }]);
    pluginFacade.connect();
  };


  var wd_webrtc = function() {
    var facade_proxy_closed = function() {
      debug('RTCCdriver failed, cannot reach driver at ' + global_config.wsUri);
      loadUi();
      actions.start_webrtc({
        bypassTurnProbeTest: global_config.bypassTurnProbeTest,
        on_webrtc_finished: function(type) {
          if (type === 'turn_probing_failed' || type === 'cannot_connect_probes') {
            downloadDriver.call(weemo);
            wd_only({
              has_called_onRtccDriverNotStarted: true
            });
          } else {
            cb_with_init_timeout(wd_webrtc)
          }

        }
      }, global_config);
    };
    var facade_proxy_opened = function() {
      vent.once({
        event: 'facade_proxy_closed',
        action: function() {
          globalVars.state = Rtcc.STATES.NOT_CONNECTED_TO_FACADE;
          disconnectedDriverEvents();
          cb_with_init_timeout(wd_webrtc);

        }
      });
      driverFacade.open();
    };

    vent.once([{
      event: 'facade_proxy_opened',
      action: facade_proxy_opened
    }, {
      event: 'facade_proxy_closed',
      action: facade_proxy_closed
    }]);
    driverFacade.connect(global_config);
  };


  var plugin_webrtc = function() {
    var facade_proxy_closed = function() {
      debug('RTCCplugin not installed or disconnected, starting webrtc');
      loadUi();
      clearTimeout(globalVars.timeout.pluginConnect);
      actions.start_webrtc({
        bypassTurnProbeTest: global_config.bypassTurnProbeTest,
        on_webrtc_finished: function(type) {
          if (type === 'turn_probing_failed' || type === 'cannot_connect_probes') {
            downloadDriver.call(weemo);
            plugin_webrtc({
              has_called_onRtccDriverNotStarted: true
            });
          } else {
            cb_with_init_timeout(plugin_webrtc)
          }
        }
      }, global_config);
    };

    var facade_proxy_opened = function() {
      vent.once({
        event: 'facade_proxy_closed',
        action: function() {
          clearTimeout(globalVars.timeout.pluginConnect);
          globalVars.state = Rtcc.STATES.NOT_CONNECTED_TO_FACADE;
          disconnectedDriverEvents();
          cb_with_init_timeout(plugin_webrtc);
        }
      });
      pluginFacade.open();
    };

    vent.once([{
      event: 'facade_proxy_opened',
      action: facade_proxy_opened
    }, {
      event: 'facade_proxy_closed',
      action: facade_proxy_closed
    }]);
    pluginFacade.connect();
  };



  var webrtc_only = function() {
    loadUi();
    actions.start_webrtc({
      bypassTurnProbeTest: global_config.bypassTurnProbeTest,
      allow_turn_failure: true,
      on_webrtc_finished: function(type) {

        if (type === 'turn_probing_failed' || type === 'cannot_connect_probes') {
          run_client_callback(weemo, 'onWebrtcImpossibleOnThisNetwork');
          apiEvents.trigger('webrtc.missing', 'WebRTC unavailable on this network.');
        } else {
          cb_with_init_timeout(webrtc_only)
        }

      }
    }, global_config);
  };


  var modeConnectionFunction = {
    'wd_only': wd_only,
    'plugin_only': plugin_only,
    'webrtc_only': webrtc_only,
    'wd_webrtc': wd_webrtc,
    'plugin_webrtc': plugin_webrtc
  };


})(actions, this);
;
var arrayContains = function(array, obj) {
  var i = array.length;
  while (i--) {
    if (array[i] === obj) {
      return true;
    }
  }
  return false;
};
;
function arrayFilter(arr, fun) {
  if (!Array.prototype.filter) {
    var t = Object(this);
    var len = arr.length >>> 0;

    // NOTE : fix to avoid very long loop on negative length value
    if (len > arr.length || typeof fun != 'function') {
      throw new TypeError();
    }

    var res = [];
    for (var i = 0; i < len; i++) {
      if (i in arr) {
        var val = arr[i];
        if (fun.call(undefined, val, i, arr))
          res.push(val);
      }
    }
    return res;
  } else {
    return arr.filter(fun)
  }

}
;
// Production steps of ECMA-262, Edition 5, 15.4.4.18
// Reference: http://es5.github.com/#x15.4.4.18
var arrayForEach = function(array, callback, thisArg) {

  var T, k;

  if (array === null) {
    throw new TypeError(" array is null or not defined");
  }

  // 1. Let O be the result of calling ToObject passing the |this| value as the argument.
  var O = Object(array);

  // 2. Let lenValue be the result of calling the Get internal method of O with the argument "length".
  // 3. Let len be ToUint32(lenValue).
  var len = O.length >>> 0;

  // 4. If IsCallable(callback) is false, throw a TypeError exception.
  // See: http://es5.github.com/#x9.11
  if (typeof callback !== "function") {
    throw new TypeError(callback + " is not a function");
  }

  // 5. If thisArg was supplied, let T be thisArg; else let T be undefined.
  if (thisArg) {
    T = thisArg;
  }

  // 6. Let k be 0
  k = 0;

  // 7. Repeat, while k < len
  while (k < len) {

    var kValue;

    // a. Let Pk be ToString(k).
    //   This is implicit for LHS operands of the in operator
    // b. Let kPresent be the result of calling the HasProperty internal method of O with argument Pk.
    //   This step can be combined with c
    // c. If kPresent is true, then
    if (k in O) {

      // i. Let kValue be the result of calling the Get internal method of O with argument Pk.
      kValue = O[k];

      // ii. Call the Call internal method of callback with T as the this value and
      // argument list containing kValue, k, and O.
      callback.call(T, kValue, k, O);
    }

    // d. Increase k by 1.
    k++;
  }
  // 8. return undefined
};
;
/*\
|*|
|*|  Base64 / binary data / UTF-8 strings utilities
|*|
|*|  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Base64_encoding_and_decoding
|*|
\*/

/* Array of bytes to base64 string decoding */

function b64ToUint6(nChr) {

  return nChr > 64 && nChr < 91 ?
    nChr - 65 : nChr > 96 && nChr < 123 ?
    nChr - 71 : nChr > 47 && nChr < 58 ?
    nChr + 4 : nChr === 43 ?
    62 : nChr === 47 ?
    63 :
    0;

}

function base64DecToArr(sBase64, nBlocksSize) {

  var
    sB64Enc = sBase64.replace(/[^A-Za-z0-9\+\/]/g, ""),
    nInLen = sB64Enc.length,
    nOutLen = nBlocksSize ? Math.ceil((nInLen * 3 + 1 >> 2) / nBlocksSize) * nBlocksSize : nInLen * 3 + 1 >> 2,
    taBytes = new Uint8Array(nOutLen);

  for (var nMod3, nMod4, nUint24 = 0, nOutIdx = 0, nInIdx = 0; nInIdx < nInLen; nInIdx++) {
    nMod4 = nInIdx & 3;
    nUint24 |= b64ToUint6(sB64Enc.charCodeAt(nInIdx)) << 18 - 6 * nMod4;
    if (nMod4 === 3 || nInLen - nInIdx === 1) {
      for (nMod3 = 0; nMod3 < 3 && nOutIdx < nOutLen; nMod3++, nOutIdx++) {
        taBytes[nOutIdx] = nUint24 >>> (16 >>> nMod3 & 24) & 255;
      }
      nUint24 = 0;

    }
  }

  return taBytes;
}

/* Base64 string to array encoding */

function uint6ToB64(nUint6) {

  return nUint6 < 26 ?
    nUint6 + 65 : nUint6 < 52 ?
    nUint6 + 71 : nUint6 < 62 ?
    nUint6 - 4 : nUint6 === 62 ?
    43 : nUint6 === 63 ?
    47 :
    65;

}

function base64EncArr(aBytes) {

  var nMod3 = 2,
    sB64Enc = "";

  for (var nLen = aBytes.length, nUint24 = 0, nIdx = 0; nIdx < nLen; nIdx++) {
    nMod3 = nIdx % 3;
    //Add a new line
    //Removed to be consistant with other base64 implementations (modP)
    //if (nIdx > 0 && (nIdx * 4 / 3) % 76 === 0) { sB64Enc += "\r\n"; }
    nUint24 |= aBytes[nIdx] << (16 >>> nMod3 & 24);
    if (nMod3 === 2 || aBytes.length - nIdx === 1) {
      sB64Enc += String.fromCharCode(uint6ToB64(nUint24 >>> 18 & 63), uint6ToB64(nUint24 >>> 12 & 63), uint6ToB64(nUint24 >>> 6 & 63), uint6ToB64(nUint24 & 63));
      nUint24 = 0;
    }
  }

  return sB64Enc.substr(0, sB64Enc.length - 2 + nMod3) + (nMod3 === 2 ? '' : nMod3 === 1 ? '=' : '==');

}

/* UTF-8 array to DOMString and vice versa */

function UTF8ArrToStr(aBytes) {

  var sView = "";

  for (var nPart, nLen = aBytes.length, nIdx = 0; nIdx < nLen; nIdx++) {
    nPart = aBytes[nIdx];
    sView += String.fromCharCode(
      nPart > 251 && nPart < 254 && nIdx + 5 < nLen ? /* six bytes */
      /* (nPart - 252 << 32) is not possible in ECMAScript! So...: */
      (nPart - 252) * 1073741824 + (aBytes[++nIdx] - 128 << 24) + (aBytes[++nIdx] - 128 << 18) + (aBytes[++nIdx] - 128 << 12) + (aBytes[++nIdx] - 128 << 6) + aBytes[++nIdx] - 128 : nPart > 247 && nPart < 252 && nIdx + 4 < nLen ? /* five bytes */
      (nPart - 248 << 24) + (aBytes[++nIdx] - 128 << 18) + (aBytes[++nIdx] - 128 << 12) + (aBytes[++nIdx] - 128 << 6) + aBytes[++nIdx] - 128 : nPart > 239 && nPart < 248 && nIdx + 3 < nLen ? /* four bytes */
      (nPart - 240 << 18) + (aBytes[++nIdx] - 128 << 12) + (aBytes[++nIdx] - 128 << 6) + aBytes[++nIdx] - 128 : nPart > 223 && nPart < 240 && nIdx + 2 < nLen ? /* three bytes */
      (nPart - 224 << 12) + (aBytes[++nIdx] - 128 << 6) + aBytes[++nIdx] - 128 : nPart > 191 && nPart < 224 && nIdx + 1 < nLen ? /* two bytes */
      (nPart - 192 << 6) + aBytes[++nIdx] - 128 : /* nPart < 127 ? */ /* one byte */
      nPart
    );
  }

  return sView;

}

function strToUTF8Arr(sDOMStr) {

  var aBytes, nChr, nStrLen = sDOMStr.length,
    nArrLen = 0;

  /* mapping... */

  for (var nMapIdx = 0; nMapIdx < nStrLen; nMapIdx++) {
    nChr = sDOMStr.charCodeAt(nMapIdx);
    nArrLen += nChr < 0x80 ? 1 : nChr < 0x800 ? 2 : nChr < 0x10000 ? 3 : nChr < 0x200000 ? 4 : nChr < 0x4000000 ? 5 : 6;
  }

  aBytes = new Uint8Array(nArrLen);

  /* transcription... */

  for (var nIdx = 0, nChrIdx = 0; nIdx < nArrLen; nChrIdx++) {
    nChr = sDOMStr.charCodeAt(nChrIdx);
    if (nChr < 128) {
      /* one byte */
      aBytes[nIdx++] = nChr;
    } else if (nChr < 0x800) {
      /* two bytes */
      aBytes[nIdx++] = 192 + (nChr >>> 6);
      aBytes[nIdx++] = 128 + (nChr & 63);
    } else if (nChr < 0x10000) {
      /* three bytes */
      aBytes[nIdx++] = 224 + (nChr >>> 12);
      aBytes[nIdx++] = 128 + (nChr >>> 6 & 63);
      aBytes[nIdx++] = 128 + (nChr & 63);
    } else if (nChr < 0x200000) {
      /* four bytes */
      aBytes[nIdx++] = 240 + (nChr >>> 18);
      aBytes[nIdx++] = 128 + (nChr >>> 12 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 6 & 63);
      aBytes[nIdx++] = 128 + (nChr & 63);
    } else if (nChr < 0x4000000) {
      /* five bytes */
      aBytes[nIdx++] = 248 + (nChr >>> 24);
      aBytes[nIdx++] = 128 + (nChr >>> 18 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 12 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 6 & 63);
      aBytes[nIdx++] = 128 + (nChr & 63);
    } else /* if (nChr <= 0x7fffffff) */ {
      /* six bytes */
      aBytes[nIdx++] = 252 + /* (nChr >>> 32) is not possible in ECMAScript! So...: */ (nChr / 1073741824);
      aBytes[nIdx++] = 128 + (nChr >>> 24 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 18 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 12 & 63);
      aBytes[nIdx++] = 128 + (nChr >>> 6 & 63);
      aBytes[nIdx++] = 128 + (nChr & 63);
    }
  }

  return aBytes;

}
;
var bindObjectToVent = function(object, ventInstance) {
  object.on = ventInstance.on.bind(ventInstance);
  object.off = ventInstance.off.bind(ventInstance);
  object.onAll = ventInstance.onAll.bind(ventInstance);
  object.offAll = ventInstance.offAll.bind(ventInstance);
  object.trigger = ventInstance.trigger.bind(ventInstance);
}
;
// via http://stackoverflow.com/a/728694/22617
function clone(obj) {
  // Handle the 3 simple types, and null or undefined
  if (null === obj || "object" !== typeof obj) {
    return obj;
  }

  var copy;

  // Handle Date
  if (obj instanceof Date) {
    copy = new Date();
    copy.setTime(obj.getTime());
    return copy;
  }

  // Handle Array
  if (obj instanceof Array) {
    copy = [];
    for (var i = 0, len = obj.length; i < len; i++) {
      copy[i] = clone(obj[i]);
    }
    return copy;
  }

  // Handle Object
  if (obj instanceof Object) {
    copy = {};
    for (var attr in obj) {
      if (obj.hasOwnProperty(attr)) {
        copy[attr] = clone(obj[attr]);
      }
    }
    return copy;
  }

  throw new Error('Unable to copy obj! Its type isn\'t supported.');
}
;
var new_cross_domain_request = function() {
  var xdr = null;
  if (window.XDomainRequest) {
    xdr = new XDomainRequest();
  } else if (window.XMLHttpRequest) {
    xdr = new XMLHttpRequest();
  } else {
    debug("Your browser does not support AJAX cross-domain!");
  }
  return xdr;
};
;
var debug = function(txt, debug_options) {
  debug_options = debug_options || {};
  var header = debug_options.header || false;
  var show_on_debug_level = debug_options.show_on_debug_level;
  if (show_on_debug_level === undefined) {
    show_on_debug_level = 1;
  }
  if (Number(global_config.debugLevel) >= show_on_debug_level) {
    if (header) {
      Rtcc._safelog(header);
    }
    Rtcc._safelog("instance:" + global_config.instance + "   " + txt);
  }
};
;
var XmlDoc = function(xml) {
  if (window.DOMParser) {
    parser = new DOMParser();
    xmlDoc = parser.parseFromString(xml, "text/xml");
  } else { // Internet Explorer
    xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
    xmlDoc.async = false;
    xmlDoc.loadXML(xml);
  }
  return xmlDoc;
};
;
var generateSuffix = function() {
  var sightcallSufix = localStorage.getItem('sightcall_suffix');
  if (sightcallSufix) {
    return sightcallSufix;
  } else {
    sightcallSufix = randomString(16);
    localStorage.setItem('sightcall_suffix', sightcallSufix);
    return sightcallSufix;
  }
};
;
var getPeerConnectionConfig = function(turn) {
  var iceConfig = global_config.iceConfig;
  var pcConfig = {
    "iceServers": []
  };

  var newIceConfig = [];
  for (var i = 0; i < iceConfig.length; i++) {
    newIceConfig.push(iceConfig[i].replace('[turn_candidate]', turn));
  }

  var iceServers = createIceServers(newIceConfig, 'weemo', 'weemo');
  if (iceServers !== null) {
    pcConfig.iceServers = pcConfig.iceServers.concat(iceServers);
  }

  return pcConfig;
};
;
var getSuffix = function() {
  if (global_config.rtccUserType !== "external") {
    debug('This function is only applicable to rtccUserType external');
    return false;
  }

  var suffix = localStorage.getItem('sightcall_suffix');


  if (!suffix) {
    debug("Sufix has not yet been generated, it is generated after calling rtcc.initialize");
    return false;
  }

  return suffix;

};
;
var isArray = function(arg) {
  return Object.prototype.toString.call(arg) === '[object Array]';
};
;
var load_configs = function(data, mgmt_replacements) {
  var config = get_global_config_defaults(mgmt_replacements);

  config.appId = data[0];
  globalVars.token = data[1];

  config.rtccUserType = data[2];
  if (typeof data[3] === "object") {
    config = Rtcc.merge(config, data[3]);
  } else {
    if (typeof data[3] === 'string') {
      config.hap = data[3];
    }
    if (data[4] !== undefined) {
      config.debugLevel = Number(data[4]);
    }
    if (data[5] !== undefined) {
      config.displayName = data[5];
    }

    if (data[6] !== undefined) {
      config.useJquery = data[6];
    }
    config.defaultStyle = data[7] !== undefined ? data[7] : true;
    config = Rtcc.merge(config, data[8]);

  }
  config.useJquery = false;
  return config;
};
;
var load_script = function(src, callback) {
  var script = document.createElement("script");
  script.src = src;
  script.onload = function() {
    if (callback) callback();
  };

  var head = document.getElementsByTagName("head")[0];
  head.appendChild(script);

};
;
Rtcc.merge = function() {
  var obj = {},
    i = 0,
    il = arguments.length,
    key;
  for (; i < il; i++) {
    for (key in arguments[i]) {
      if (arguments[i].hasOwnProperty(key)) {
        obj[key] = arguments[i][key];
      }
    }
  }
  return obj;
};
;
var new_ajax_request = function() {
  if (window.XMLHttpRequest) { // code for IE7+, Firefox, Chrome, Opera, Safari
    return new XMLHttpRequest();
  } else { // code for IE6, IE5
    return new ActiveXObject("Microsoft.XMLHTTP");
  }
};
;
function objectForEach(object, callback) {
  for (var k in object) {
    if (object.hasOwnProperty(k)) callback(k, object[k])
  }
}
;
if (!Object.keys) {
  Object.keys = (function() {
    'use strict';
    var hasOwnProperty = Object.prototype.hasOwnProperty,
      hasDontEnumBug = !({
        toString: null
      }).propertyIsEnumerable('toString'),
      dontEnums = [
        'toString',
        'toLocaleString',
        'valueOf',
        'hasOwnProperty',
        'isPrototypeOf',
        'propertyIsEnumerable',
        'constructor'
      ],
      dontEnumsLength = dontEnums.length;

    return function(obj) {
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
        throw new TypeError('Object.keys called on non-object');
      }

      var result = [],
        prop, i;

      for (prop in obj) {
        if (hasOwnProperty.call(obj, prop)) {
          result.push(prop);
        }
      }

      if (hasDontEnumBug) {
        for (i = 0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) {
            result.push(dontEnums[i]);
          }
        }
      }
      return result;
    };
  }());
}
;
var parseHapXml = function(xml) {
  var tuneName,
    tuneAddress,
    xmlDoc = new XmlDoc(xml);

  var return_obj = {};
  return_obj.tuntab = [];
  var t = xmlDoc.getElementsByTagName("techdomain")[0];
  if (t !== undefined) {
    return_obj.techdomain = xmlDoc.getElementsByTagName("techdomain")[0].childNodes[0].nodeValue;
  }
  var l = xmlDoc.getElementsByTagName("local")[0];
  if (l !== undefined) {
    return_obj.localAddress = xmlDoc.getElementsByTagName("local")[0].getAttribute('addr');
  }
  var nbTune = xmlDoc.getElementsByTagName("tun").length;
  if (nbTune !== undefined) {
    for (var i = 0; i < nbTune; i += 1) {
      if (xmlDoc.getElementsByTagName("tun")[i].getElementsByTagName("probews")[0]) {
        tuneName = xmlDoc.getElementsByTagName("tun")[i].getAttribute('name');
        tuneAddress = xmlDoc.getElementsByTagName("tun")[i].getElementsByTagName("probews")[0].getAttribute('addr');
        var port = xmlDoc.getElementsByTagName("tun")[i].getElementsByTagName("probews")[0].getAttribute('port');
        var webRtcNode = xmlDoc.getElementsByTagName("tun")[i].getElementsByTagName("webrtc")[0];
        var turnAddress = xmlDoc.getElementsByTagName("tun")[i].getElementsByTagName("probe")[0].getAttribute('addr');


        return_obj.tuntab.push({
          name: tuneName,
          address: tuneAddress,
          port: port,
          webrtc: webRtcNode.getAttribute('addr') + ":" + webRtcNode.getAttribute('port'),
          turn: turnAddress
        });
      }
    }
  }
  return return_obj;
};
;
//Uint8Array polyfill
(function() {
  try {
    var a = new Uint8Array(1);
    return; //no need
  } catch (e) {}

  function subarray(start, end) {
    return this.slice(start, end);
  }

  function set_(array, offset) {
    if (arguments.length < 2) offset = 0;
    for (var i = 0, n = array.length; i < n; ++i, ++offset)
      this[offset] = array[i] & 0xFF;
  }

  // we need typed arrays
  function TypedArray(arg1) {
    var result;
    if (typeof arg1 === "number") {
      result = new Array(arg1);
      for (var i = 0; i < arg1; ++i)
        result[i] = 0;
    } else
      result = arg1.slice(0);
    result.subarray = subarray;
    result.buffer = result;
    result.byteLength = result.length;
    result.set = set_;
    if (typeof arg1 === "object" && arg1.buffer)
      result.buffer = arg1.buffer;

    return result;
  }

  window.Uint8Array = TypedArray;
  window.Uint32Array = TypedArray;
  window.Int32Array = TypedArray;
})();
;
  function randomString(length) {
    var result = '';
    var chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for (var i = length; i > 0; --i) result += chars[Math.round(Math.random() * (chars.length - 1))];
    return result;
  }
;
var run_client_callback = function(context, call, args, default_function) {

  if (typeof context[call] === "function") {
    try {
      debug("WARNING " + call + " is depreciated please use events instead, see javascript api documentation `rtcc.on('event_name', cb)`");
      context[call].apply(context, args);
    } catch (error) {
      debug("error in callback function");
      debug(error.stack);
    }
  } else if (typeof default_function === "function") {
    debug("callback " + call + " not present, running default function");
    default_function();
  } else {
    debug("callback " + call + " not present");
  }
};
;
function statusCallEventName(status) {
  if (status === 'terminated') status = 'terminate';
  if (status === 'createdCall') status = 'create';
  return status;
}
;
var strpos = function(haystack, needle, offset) {
  var i = String(haystack).indexOf(needle, (offset || 0));
  if (i === -1) {
    i = false;
  }
  return i;
};
;
var system_info = function() {
  function init() {
    system_info.data = {};
    var unknown = 'Unbekannt';
    // screen
    var width,
      height;
    if (screen.width) {
      width = (screen.width) ? screen.width : '';
      height = (screen.height) ? screen.height : '';
      screenSize = width + " x " + height;
    }

    //browser
    var nVer = navigator.appVersion;
    var nAgt = navigator.userAgent;
    system_info.data.browser = navigator.appName;
    system_info.data.browserVersion = '' + parseFloat(navigator.appVersion);
    var majorVersion = parseInt(navigator.appVersion, 10);
    var nameOffset, verOffset, ix;

    // Opera
    if ((verOffset = nAgt.indexOf('Opera')) != -1) {
      system_info.data.browser = 'Opera';
      system_info.data.browserVersion = nAgt.substring(verOffset + 6);
      if ((verOffset = nAgt.indexOf('Version')) != -1) {
        system_info.data.browserVersion = nAgt.substring(verOffset + 8);
      }
    }
    // MSIE
    else if ((verOffset = nAgt.indexOf('MSIE')) != -1) {
      system_info.data.browser = 'Microsoft Internet Explorer';
      system_info.data.browserVersion = nAgt.substring(verOffset + 5);
    }

    //IE11
    else if ((verOffset = nAgt.indexOf('Trident/7.')) != -1) {
      system_info.data.browser = 'Microsoft Internet Explorer';
      if ((verOffset = nAgt.indexOf('rv:')) != -1) {
        system_info.data.browserVersion = nAgt.substring(verOffset + 3, verOffset + 7);
      }
    }
    // Chrome
    else if ((verOffset = nAgt.indexOf('Chrome')) != -1) {
      system_info.data.browser = 'Chrome';
      system_info.data.browserVersion = nAgt.substring(verOffset + 7);
    }
    // Safari
    else if ((verOffset = nAgt.indexOf('Safari')) != -1) {
      system_info.data.browser = 'Safari';
      system_info.data.browserVersion = nAgt.substring(verOffset + 7);
      if ((verOffset = nAgt.indexOf('Version')) != -1) {
        system_info.data.browserVersion = nAgt.substring(verOffset + 8);
      }
    }
    // Firefox
    else if ((verOffset = nAgt.indexOf('Firefox')) != -1) {
      system_info.data.browser = 'Firefox';
      system_info.data.browserVersion = nAgt.substring(verOffset + 8);
    }
    // Other browsers
    else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) < (verOffset = nAgt.lastIndexOf('/'))) {
      system_info.data.browser = nAgt.substring(nameOffset, verOffset);
      system_info.data.browserVersion = nAgt.substring(verOffset + 1);
      if (system_info.data.browser.toLowerCase() == system_info.data.browser.toUpperCase()) {
        system_info.data.browser = navigator.appName;
      }
    }
    // trim the version string
    if ((ix = system_info.data.browserVersion.indexOf(';')) != -1) system_info.data.browserVersion = system_info.data.browserVersion.substring(0, ix);
    if ((ix = system_info.data.browserVersion.indexOf(' ')) != -1) system_info.data.browserVersion = system_info.data.browserVersion.substring(0, ix);

    majorVersion = parseInt('' + system_info.data.browserVersion, 10);
    if (isNaN(majorVersion)) {
      system_info.data.browserVersion = '' + parseFloat(navigator.appVersion);
      majorVersion = parseInt(navigator.appVersion, 10);
    }

    // mobile version
    system_info.data.mobile = /Mobile|mini|Fennec|Android|iP(ad|od|hone)/.test(nVer);

    // cookie
    system_info.data.cookieEnabled = (navigator.cookieEnabled) ? true : false;

    if (typeof navigator.cookieEnabled == 'undefined' && !cookieEnabled) {
      document.cookie = 'testcookie';
      system_info.data.cookieEnabled = (document.cookie.indexOf('testcookie') != -1) ? true : false;
    }

    // system
    system_info.data.os = unknown;
    var clientStrings = [{
      s: 'Windows 3.11',
      r: /Win16/
    }, {
      s: 'Windows 95',
      r: /(Windows 95|Win95|Windows_95)/
    }, {
      s: 'Windows 98',
      r: /(Windows 98|Win98)/
    }, {
      s: 'Windows CE',
      r: /Windows CE/
    }, {
      s: 'Windows 2000',
      r: /(Windows NT 5.0|Windows 2000)/
    }, {
      s: 'Windows XP',
      r: /(Windows NT 5.1|Windows XP)/
    }, {
      s: 'Windows Server 2003',
      r: /Windows NT 5.2/
    }, {
      s: 'Windows Vista',
      r: /Windows NT 6.0/
    }, {
      s: 'Windows 7',
      r: /(Windows 7|Windows NT 6.1)/
    }, {
      s: 'Windows 8.1',
      r: /(Windows 8.1|Windows NT 6.3)/
    }, {
      s: 'Windows 8',
      r: /(Windows 8|Windows NT 6.2)/
    }, {
      s: 'Windows NT 4.0',
      r: /(Windows NT 4.0|WinNT4.0|WinNT|Windows NT)/
    }, {
      s: 'Windows ME',
      r: /Windows ME/
    }, {
      s: 'Android',
      r: /Android/
    }, {
      s: 'Open BSD',
      r: /OpenBSD/
    }, {
      s: 'Sun OS',
      r: /SunOS/
    }, {
      s: 'Linux',
      r: /(Linux|X11)/
    }, {
      s: 'iOS',
      r: /(iPhone|iPad|iPod)/
    }, {
      s: 'Mac OS X',
      r: /Mac OS X/
    }, {
      s: 'Mac OS',
      r: /(MacPPC|MacIntel|Mac_PowerPC|Macintosh)/
    }, {
      s: 'QNX',
      r: /QNX/
    }, {
      s: 'UNIX',
      r: /UNIX/
    }, {
      s: 'BeOS',
      r: /BeOS/
    }, {
      s: 'OS/2',
      r: /OS\/2/
    }, {
      s: 'Search Bot',
      r: /(nuhk|Googlebot|Yammybot|Openbot|Slurp|MSNBot|Ask Jeeves\/Teoma|ia_archiver)/
    }];
    for (var id in clientStrings) {
      var cs = clientStrings[id];
      if (cs.r.test(nAgt)) {
        system_info.data.os = cs.s;
        break;
      }
    }

    system_info.data.osVersion = unknown;
    if (/Windows/.test(system_info.data.os)) {
      system_info.data.osVersion = /Windows (.*)/.exec(system_info.data.os)[1];
      system_info.data.os = 'Windows';
    }

    switch (system_info.data.os) {
      case 'Mac OS X':
        var osVersion = /Mac OS X (10[\.\_\d]+)/.exec(nAgt);
        if (osVersion) {
          system_info.data.osVersion = osVersion[1];
        }
        break;

      case 'Android':
        system_info.data.osVersion = /Android ([\.\_\d]+)/.exec(nAgt)[1];
        break;

      case 'iOS':
        system_info.data.osVersion = /OS (\d+)_(\d+)_?(\d+)?/.exec(nVer);
        system_info.data.osVersion = system_info.data.osVersion[1] + '.' + system_info.data.osVersion[2] + '.' + (system_info.data.osVersion[3] | 0);
        break;

    }
    if (system_info.data.browser === "Microsoft Internet Explorer" && system_info.data.browserVersion < 12) {
      system_info.data.useSockets = false;
      system_info.data.downloadTimeoutValue = 20000;
    } else {
      system_info.data.useSockets = true;
      system_info.data.downloadTimeoutValue = 8000;
    }
  }

  if (system_info.data === undefined) {
    init();
  }
  return system_info.data;
};
;
function triggerFacadeProxyClosed() {
  if (globalVars.state !== Rtcc.STATES.DESTROYED) vent.trigger('facade_proxy_closed');
}
;
uniqid = function() {
  return (new Date()).getTime() % (2147483648 - 1);
};
;
var wd_supports_os = function(os, force) {
  return force || (os !== "linux" && os !== "unix" && os !== "Linux" && os !== "Unix");
};
;
var webrtc_compliant = function() {
  return ((system_info().browser === "Chrome" || global_config.forceWebRtcCompliant) && !global_config.forceNotWebRtcCompliant);
};
;
if (!String.prototype.encodeHTML) {
  String.prototype.encodeHTML = function() {
    return this.replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  };
}

if (!String.prototype.decodeHTML) {
  String.prototype.decodeHTML = function() {
    return this.replace(/&apos;/g, "'")
      .replace(/&quot;/g, '"')
      .replace(/&gt;/g, '>')
      .replace(/&lt;/g, '<')
      .replace(/&amp;/g, '&');
  };
}
;
/* istanbul ignore next */
var JXON = (function() {
  var module = {};

  function xml2json(xml, tab) {
    var X = {
      toObj: function(xml) {
        var o = {};
        if (xml.nodeType == 1) { // element node ..
          if (xml.attributes.length) // element with attributes  ..
            for (var i = 0; i < xml.attributes.length; i++)
            o["@" + xml.attributes[i].nodeName] = (xml.attributes[i].nodeValue || "").toString();
          if (xml.firstChild) { // element has child nodes ..
            var textChild = 0,
              cdataChild = 0,
              hasElementChild = false;
            for (var n = xml.firstChild; n; n = n.nextSibling) {
              if (n.nodeType == 1) hasElementChild = true;
              else if (n.nodeType == 3 && n.nodeValue.match(/[^ \f\n\r\t\v]/)) textChild++; // non-whitespace text
              else if (n.nodeType == 4) cdataChild++; // cdata section node
            }
            if (hasElementChild) {
              if (textChild < 2 && cdataChild < 2) { // structured element with evtl. a single text or/and cdata node ..
                X.removeWhite(xml);
                for (var n = xml.firstChild; n; n = n.nextSibling) {
                  if (n.nodeType == 3) // text node
                    o["#text"] = X.escape(n.nodeValue);
                  else if (n.nodeType == 4) // cdata node
                    o["#cdata"] = X.escape(n.nodeValue);
                  else if (o[n.nodeName]) { // multiple occurence of element ..
                    if (o[n.nodeName] instanceof Array)
                      o[n.nodeName][o[n.nodeName].length] = X.toObj(n);
                    else
                      o[n.nodeName] = [o[n.nodeName], X.toObj(n)];
                  } else // first occurence of element..
                    o[n.nodeName] = X.toObj(n);
                }
              } else { // mixed content
                if (!xml.attributes.length)
                  o = X.escape(X.innerXml(xml));
                else
                  o["#text"] = X.escape(X.innerXml(xml));
              }
            } else if (textChild) { // pure text
              if (!xml.attributes.length)
                o = X.escape(X.innerXml(xml));
              else
                o["#text"] = X.escape(X.innerXml(xml));
            } else if (cdataChild) { // cdata
              if (cdataChild > 1)
                o = X.escape(X.innerXml(xml));
              else
                for (var n = xml.firstChild; n; n = n.nextSibling)
                  o["#cdata"] = X.escape(n.nodeValue);
            }
          }
          if (!xml.attributes.length && !xml.firstChild) o = null;
        } else if (xml.nodeType == 9) { // document.node
          o = X.toObj(xml.documentElement);
        } else
          alert("unhandled node type: " + xml.nodeType);
        return o;
      },
      toJson: function(o, name, ind) {
        var json = name ? ("\"" + name + "\"") : "";
        if (o instanceof Array) {
          for (var i = 0, n = o.length; i < n; i++)
            o[i] = X.toJson(o[i], "", ind + "\t");
          json += (name ? ":[" : "[") + (o.length > 1 ? ("\n" + ind + "\t" + o.join(",\n" + ind + "\t") + "\n" + ind) : o.join("")) + "]";
        } else if (o == null)
          json += (name && ":") + "null";
        else if (typeof(o) == "object") {
          var arr = [];
          for (var m in o)
            arr[arr.length] = X.toJson(o[m], m, ind + "\t");
          json += (name ? ":{" : "{") + (arr.length > 1 ? ("\n" + ind + "\t" + arr.join(",\n" + ind + "\t") + "\n" + ind) : arr.join("")) + "}";
        } else if (typeof(o) == "string")
          json += (name && ":") + "\"" + o.toString() + "\"";
        else
          json += (name && ":") + o.toString();
        return json;
      },
      innerXml: function(node) {
        var s = "";
        if ("innerHTML" in node)
          s = node.innerHTML;
        else {
          var asXml = function(n) {
            var s = "";
            if (n.nodeType == 1) {
              s += "<" + n.nodeName;
              for (var i = 0; i < n.attributes.length; i++)
                s += " " + n.attributes[i].nodeName + "=\"" + (n.attributes[i].nodeValue || "").toString() + "\"";
              if (n.firstChild) {
                s += ">";
                for (var c = n.firstChild; c; c = c.nextSibling)
                  s += asXml(c);
                s += "</" + n.nodeName + ">";
              } else
                s += "/>";
            } else if (n.nodeType == 3)
              s += n.nodeValue;
            else if (n.nodeType == 4)
              s += "<![CDATA[" + n.nodeValue + "]]>";
            return s;
          };
          for (var c = node.firstChild; c; c = c.nextSibling)
            s += asXml(c);
        }
        return s;
      },
      escape: function(txt) {
        return txt.replace(/[\\]/g, "\\\\")
          .replace(/[\"]/g, '\\"')
          .replace(/[\n]/g, '\\n')
          .replace(/[\r]/g, '\\r');
      },
      removeWhite: function(e) {
        e.normalize();
        for (var n = e.firstChild; n;) {
          if (n.nodeType == 3) { // text node
            if (!n.nodeValue.match(/[^ \f\n\r\t\v]/)) { // pure whitespace text node
              var nxt = n.nextSibling;
              e.removeChild(n);
              n = nxt;
            } else
              n = n.nextSibling;
          } else if (n.nodeType == 1) { // element node
            X.removeWhite(n);
            n = n.nextSibling;
          } else // any other node
            n = n.nextSibling;
        }
        return e;
      }
    };
    if (xml.nodeType == 9) // document node
      xml = xml.documentElement;
    var json = X.toJson(X.toObj(X.removeWhite(xml)), xml.nodeName, "\t");
    return "{\n" + tab + (tab ? json.replace(/\t/g, tab) : json.replace(/\t|\n/g, "")) + "\n}";
  }



  function json2xml(o, tab) {
    var toXml = function(v, name, ind) {
        var xml = "";
        if (v instanceof Array) {
          for (var i = 0, n = v.length; i < n; i++)
            xml += ind + toXml(v[i], name, ind + "\t") + "\n";
        } else if (typeof(v) == "object") {
          var hasChild = false;
          xml += ind + "<" + name;
          for (var m in v) {
            if (m.charAt(0) == "@")
              xml += " " + m.substr(1) + "=\"" + v[m].toString() + "\"";
            else
              hasChild = true;
          }
          xml += hasChild ? ">" : "/>";
          if (hasChild) {
            for (var m in v) {
              if (m == "#text")
                xml += v[m];
              else if (m == "#cdata")
                xml += "<![CDATA[" + v[m] + "]]>";
              else if (m.charAt(0) != "@")
                xml += toXml(v[m], m, ind + "\t");
            }
            xml += (xml.charAt(xml.length - 1) == "\n" ? ind : "") + "</" + name + ">";
          }
        } else {
          xml += ind + "<" + name + ">" + v.toString() + "</" + name + ">";
        }
        return xml;
      },
      xml = "";
    for (var m in o)
      xml += toXml(o[m], m, "");
    return tab ? xml.replace(/\t/g, tab) : xml.replace(/\t|\n/g, "");
  }



  module.xmlString2jsonObject = function(xmlString) {
    xmlDoc = XMLfromString(xmlString);
    return module.xmlDoc2jsonObject(xmlDoc);
  };

  module.xmlDoc2jsonObject = function(xmlDoc) {
    return JSON.parse(xml2json(xmlDoc, ''));
  };

  module.jsonObject2xmlString = function(jsonObject) {
    return json2xml(jsonObject, '');
  };

  var XMLfromString = function(xmlString) {
    return XmlDoc(xmlString, "text/xml");
  };

  return module;
})();
;
var StateManager = function(statesToReachArray, callback, callOnce) {
  callOnce = callOnce || false;
  var hasStateBeenCalled = {};
  var callbackCalled = false;

  for (var i = 0; i < statesToReachArray.length; i++) {
    hasStateBeenCalled[statesToReachArray[i]] = false;
  }
  var context = null;

  this.reach = function(state) {
    if (hasStateBeenCalled[state] === undefined) {
      throw new Error("unknown state " + state);
    }
    hasStateBeenCalled[state] = true;
    return this;
  }

  this.tryRun = function() {
    for (var i = 0; i < statesToReachArray.length; i++) {
      if (hasStateBeenCalled[statesToReachArray[i]] === false) {
        return false;
      }
    }
    if (!(callOnce && callbackCalled)) {
      callback();
      callbackCalled = true;
    }
    return true;
  }

  this.setCallback = function(cb, callOnceOption) {
    callOnce = callOnceOption || false;
    callback = cb;
    return this
  }
}
;
var sdpParser = {};
(function e(t, n, r) {
  function s(o, u) {
    if (!n[o]) {
      if (!t[o]) {
        var a = typeof require == "function" && require;
        if (!u && a) return a(o, !0);
        if (i) return i(o, !0);
        var f = new Error("Cannot find module '" + o + "'");
        throw f.code = "MODULE_NOT_FOUND", f
      }
      var l = n[o] = {
        exports: {}
      };
      t[o][0].call(l.exports, function(e) {
        var n = t[o][1][e];
        return s(n ? n : e)
      }, l, l.exports, e, t, n, r)
    }
    return n[o].exports
  }
  var i = typeof require == "function" && require;
  for (var o = 0; o < r.length; o++) s(r[o]);
  return s
})({
  1: [function(require, module, exports) {
    (function(sdpParser) {
      var parser = require('sdp-transform');
      sdpParser.parseSDP = parser.parse;
      sdpParser.writeSDP = parser.write;
      sdpParser.parseFmtpConfig = parser.parseFmtpConfig;
      sdpParser.parsePayloads = parser.parsePayloads;
      sdpParser.parseRemoteCandidates = parser.parseRemoteCandidates;
    })(sdpParser);

  }, {
    "sdp-transform": 3
  }],
  2: [function(require, module, exports) {
    var grammar = module.exports = {
      v: [{
        name: 'version',
        reg: /^(\d*)$/
      }],
      o: [{ //o=- 20518 0 IN IP4 203.0.113.1
        // NB: sessionId will be a String in most cases because it is huge
        name: 'origin',
        reg: /^(\S*) (\d*) (\d*) (\S*) IP(\d) (\S*)/,
        names: ['username', 'sessionId', 'sessionVersion', 'netType', 'ipVer', 'address'],
        format: "%s %s %d %s IP%d %s"
      }],
      // default parsing of these only (though some of these feel outdated)
      s: [{
        name: 'name'
      }],
      i: [{
        name: 'description'
      }],
      u: [{
        name: 'uri'
      }],
      e: [{
        name: 'email'
      }],
      p: [{
        name: 'phone'
      }],
      z: [{
        name: 'timezones'
      }], // TODO: this one can actually be parsed properly..
      r: [{
        name: 'repeats'
      }], // TODO: this one can also be parsed properly
      //k: [{}], // outdated thing ignored
      t: [{ //t=0 0
        name: 'timing',
        reg: /^(\d*) (\d*)/,
        names: ['start', 'stop'],
        format: "%d %d"
      }],
      c: [{ //c=IN IP4 10.47.197.26
        name: 'connection',
        reg: /^IN IP(\d) (\S*)/,
        names: ['version', 'ip'],
        format: "IN IP%d %s"
      }],
      b: [{ //b=AS:4000
        push: 'bandwidth',
        reg: /^(TIAS|AS|CT|RR|RS):(\d*)/,
        names: ['type', 'limit'],
        format: "%s:%s"
      }],
      m: [{ //m=video 51744 RTP/AVP 126 97 98 34 31
        // NB: special - pushes to session
        // TODO: rtp/fmtp should be filtered by the payloads found here?
        reg: /^(\w*) (\d*) ([\w\/]*)(?: (.*))?/,
        names: ['type', 'port', 'protocol', 'payloads'],
        format: "%s %d %s %s"
      }],
      a: [{ //a=rtpmap:110 opus/48000/2
        push: 'rtp',
        reg: /^rtpmap:(\d*) ([\w\-]*)\/(\d*)(?:\s*\/(\S*))?/,
        names: ['payload', 'codec', 'rate', 'encoding'],
        format: function(o) {
          return (o.encoding) ?
            "rtpmap:%d %s/%s/%s" :
            "rtpmap:%d %s/%s";
        }
      }, { //a=fmtp:108 profile-level-id=24;object=23;bitrate=64000
        push: 'fmtp',
        reg: /^fmtp:(\d*) (\S*)/,
        names: ['payload', 'config'],
        format: "fmtp:%d %s"
      }, { //a=control:streamid=0
        name: 'control',
        reg: /^control:(.*)/,
        format: "control:%s"
      }, { //a=rtcp:65179 IN IP4 193.84.77.194
        name: 'rtcp',
        reg: /^rtcp:(\d*)(?: (\S*) IP(\d) (\S*))?/,
        names: ['port', 'netType', 'ipVer', 'address'],
        format: function(o) {
          return (o.address != null) ?
            "rtcp:%d %s IP%d %s" :
            "rtcp:%d";
        }
      }, { //a=rtcp-fb:98 trr-int 100
        push: 'rtcpFbTrrInt',
        reg: /^rtcp-fb:(\*|\d*) trr-int (\d*)/,
        names: ['payload', 'value'],
        format: "rtcp-fb:%d trr-int %d"
      }, { //a=rtcp-fb:98 nack rpsi
        push: 'rtcpFb',
        reg: /^rtcp-fb:(\*|\d*) ([\w-_]*)(?: ([\w-_]*))?/,
        names: ['payload', 'type', 'subtype'],
        format: function(o) {
          return (o.subtype != null) ?
            "rtcp-fb:%s %s %s" :
            "rtcp-fb:%s %s";
        }
      }, { //a=extmap:2 urn:ietf:params:rtp-hdrext:toffset
        //a=extmap:1/recvonly URI-gps-string
        push: 'ext',
        reg: /^extmap:([\w_\/]*) (\S*)(?: (\S*))?/,
        names: ['value', 'uri', 'config'], // value may include "/direction" suffix
        format: function(o) {
          return (o.config != null) ?
            "extmap:%s %s %s" :
            "extmap:%s %s"
        }
      }, {
        //a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:PS1uQCVeeCFCanVmcjkpPywjNWhcYD0mXXtxaVBR|2^20|1:32
        push: 'crypto',
        reg: /^crypto:(\d*) ([\w_]*) (\S*)(?: (\S*))?/,
        names: ['id', 'suite', 'config', 'sessionConfig'],
        format: function(o) {
          return (o.sessionConfig != null) ?
            "crypto:%d %s %s %s" :
            "crypto:%d %s %s";
        }
      }, { //a=setup:actpass
        name: 'setup',
        reg: /^setup:(\w*)/,
        format: "setup:%s"
      }, { //a=mid:1
        name: 'mid',
        reg: /^mid:(\w*)/,
        format: "mid:%s"
      }, { //a=ptime:20
        name: 'ptime',
        reg: /^ptime:(\d*)/,
        format: "ptime:%d"
      }, { //a=maxptime:60
        name: 'maxptime',
        reg: /^maxptime:(\d*)/,
        format: "maxptime:%d"
      }, { //a=sendrecv
        name: 'direction',
        reg: /^(sendrecv|recvonly|sendonly|inactive)/,
        format: "%s"
      }, { //a=ice-ufrag:F7gI
        name: 'iceUfrag',
        reg: /^ice-ufrag:(\S*)/,
        format: "ice-ufrag:%s"
      }, { //a=ice-pwd:x9cml/YzichV2+XlhiMu8g
        name: 'icePwd',
        reg: /^ice-pwd:(\S*)/,
        format: "ice-pwd:%s"
      }, { //a=fingerprint:SHA-1 00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33
        name: 'fingerprint',
        reg: /^fingerprint:(\S*) (\S*)/,
        names: ['type', 'hash'],
        format: "fingerprint:%s %s"
      }, {
        //a=candidate:0 1 UDP 2113667327 203.0.113.1 54400 typ host
        //a=candidate:1162875081 1 udp 2113937151 192.168.34.75 60017 typ host generation 0
        //a=candidate:3289912957 2 udp 1845501695 193.84.77.194 60017 typ srflx raddr 192.168.34.75 rport 60017 generation 0
        push: 'candidates',
        reg: /^candidate:(\S*) (\d*) (\S*) (\d*) (\S*) (\d*) typ (\S*)(?: raddr (\S*) rport (\d*))?(?: generation (\d*))?/,
        names: ['foundation', 'component', 'transport', 'priority', 'ip', 'port', 'type', 'raddr', 'rport', 'generation'],
        format: function(o) {
          var str = "candidate:%s %d %s %d %s %d typ %s";
          // NB: candidate has two optional chunks, so %void middle one if it's missing
          str += (o.raddr != null) ? " raddr %s rport %d" : "%v%v";
          if (o.generation != null) {
            str += " generation %d";
          }
          return str;
        }
      }, { //a=remote-candidates:1 203.0.113.1 54400 2 203.0.113.1 54401 ...
        name: 'remoteCandidates',
        reg: /^remote-candidates:(.*)/,
        format: "remote-candidates:%s"
      }, { //a=ice-options:google-ice
        name: 'iceOptions',
        reg: /^ice-options:(\S*)/,
        format: "ice-options:%s"
      }, { //a=ssrc:2566107569 cname:t9YU8M1UxTF8Y1A1
        push: "ssrcs",
        reg: /^ssrc:(\d*) ([\w_]*):(.*)/,
        names: ['id', 'attribute', 'value'],
        format: "ssrc:%d %s:%s"
      }, { //a=msid-semantic: WMS Jvlam5X3SX1OP6pn20zWogvaKJz5Hjf9OnlV
        name: "msidSemantic",
        reg: /^msid-semantic: (\w*) (\S*)/,
        names: ['semantic', 'token'],
        format: "msid-semantic: %s %s" // space after ":" is not accidental
      }, { //a=group:BUNDLE audio video
        push: 'groups',
        reg: /^group:(\w*) (.*)/,
        names: ['type', 'mids'],
        format: "group:%s %s"
      }, { //a=rtcp-mux
        name: 'rtcpMux',
        reg: /^(rtcp-mux)/
      }, { // any a= that we don't understand is kepts verbatim on media.invalid
        push: 'invalid',
        names: ["value"]
      }]
    };

    // set sensible defaults to avoid polluting the grammar with boring details
    arrayForEach(Object.keys(grammar), function(key) {
      var objs = grammar[key];
      arrayForEach(objs, function(obj) {
        if (!obj.reg) {
          obj.reg = /(.*)/;
        }
        if (!obj.format) {
          obj.format = "%s";
        }
      });
    });

  }, {}],
  3: [function(require, module, exports) {
    var parser = require('./parser');
    var writer = require('./writer');

    exports.write = writer;
    exports.parse = parser.parse;
    exports.parseFmtpConfig = parser.parseFmtpConfig;
    exports.parsePayloads = parser.parsePayloads;
    exports.parseRemoteCandidates = parser.parseRemoteCandidates;

  }, {
    "./parser": 4,
    "./writer": 5
  }],
  4: [function(require, module, exports) {
    var toIntIfInt = function(v) {
      return String(Number(v)) === v ? Number(v) : v;
    };

    var attachProperties = function(match, location, names, rawName) {
      if (rawName && !names) {
        location[rawName] = toIntIfInt(match[1]);
      } else {
        for (var i = 0; i < names.length; i += 1) {
          if (match[i + 1] != null) {
            location[names[i]] = toIntIfInt(match[i + 1]);
          }
        }
      }
    };

    var parseReg = function(obj, location, content) {
      var needsBlank = obj.name && obj.names;
      if (obj.push && !location[obj.push]) {
        location[obj.push] = [];
      } else if (needsBlank && !location[obj.name]) {
        location[obj.name] = {};
      }
      var keyLocation = obj.push ? {} : // blank object that will be pushed
        needsBlank ? location[obj.name] : location; // otherwise, named location or root

      attachProperties(content.match(obj.reg), keyLocation, obj.names, obj.name);

      if (obj.push) {
        location[obj.push].push(keyLocation);
      }
    };

    var grammar = require('./grammar');
    var validLine = RegExp.prototype.test.bind(/^([a-z])=(.*)/);

    exports.parse = function(sdp) {
      var session = {},
        media = [],
        location = session; // points at where properties go under (one of the above)

      // parse lines we understand
      sdp.split('\r\n').filter(validLine).forEach(function(l) {
        var type = l[0];
        var content = l.slice(2);
        if (type === 'm') {
          media.push({
            rtp: [],
            fmtp: []
          });
          location = media[media.length - 1]; // point at latest media line
        }

        for (var j = 0; j < (grammar[type] || []).length; j += 1) {
          var obj = grammar[type][j];
          if (obj.reg.test(content)) {
            return parseReg(obj, location, content);
          }
        }
      });

      session.media = media; // link it up
      return session;
    };

    var fmtpReducer = function(acc, expr) {
      var s = expr.split('=');
      if (s.length === 2) {
        acc[s[0]] = toIntIfInt(s[1]);
      }
      return acc;
    };

    exports.parseFmtpConfig = function(str) {
      return str.split(';').reduce(fmtpReducer, {});
    };

    exports.parsePayloads = function(str) {
      return str.split(' ').map(Number);
    };

    exports.parseRemoteCandidates = function(str) {
      var candidates = [];
      var parts = str.split(' ').map(toIntIfInt);
      for (var i = 0; i < parts.length; i += 3) {
        candidates.push({
          component: parts[i],
          ip: parts[i + 1],
          port: parts[i + 2]
        });
      }
      return candidates;
    };

  }, {
    "./grammar": 2
  }],
  5: [function(require, module, exports) {
    var grammar = require('./grammar');

    // customized util.format - discards excess arguments and can void middle ones
    var formatRegExp = /%[sdv%]/g;
    var format = function(formatStr) {
      var i = 1;
      var args = arguments;
      var len = args.length;
      return formatStr.replace(formatRegExp, function(x) {
        if (i >= len) {
          return x; // missing argument
        }
        var arg = args[i];
        i += 1;
        switch (x) {
          case '%%':
            return '%';
          case '%s':
            return String(arg);
          case '%d':
            return Number(arg);
          case '%v':
            return '';
        }
      });
      // NB: we discard excess arguments - they are typically undefined from makeLine
    };

    var makeLine = function(type, obj, location) {
      var str = obj.format instanceof Function ?
        (obj.format(obj.push ? location : location[obj.name])) :
        obj.format;

      var args = [type + '=' + str];
      if (obj.names) {
        for (var i = 0; i < obj.names.length; i += 1) {
          var n = obj.names[i];
          if (obj.name) {
            args.push(location[obj.name][n]);
          } else { // for mLine and push attributes
            args.push(location[obj.names[i]]);
          }
        }
      } else {
        args.push(location[obj.name]);
      }
      return format.apply(null, args);
    };

    // RFC specified order
    // TODO: extend this with all the rest
    var defaultOuterOrder = [
      'v', 'o', 's', 'i',
      'u', 'e', 'p', 'c',
      'b', 't', 'r', 'z', 'a'
    ];
    var defaultInnerOrder = ['i', 'c', 'b', 'a'];


    module.exports = function(session, opts) {
      opts = opts || {};
      // ensure certain properties exist
      if (session.version == null) {
        session.version = 0; // "v=0" must be there (only defined version atm)
      }
      if (session.name == null) {
        session.name = " "; // "s= " must be there if no meaningful name set
      }
      session.media.forEach(function(mLine) {
        if (mLine.payloads == null) {
          mLine.payloads = "";
        }
      });

      var outerOrder = opts.outerOrder || defaultOuterOrder;
      var innerOrder = opts.innerOrder || defaultInnerOrder;
      var sdp = [];

      // loop through outerOrder for matching properties on session
      outerOrder.forEach(function(type) {
        grammar[type].forEach(function(obj) {
          if (obj.name in session) {
            sdp.push(makeLine(type, obj, session));
          } else if (obj.push in session) {
            session[obj.push].forEach(function(el) {
              sdp.push(makeLine(type, obj, el));
            });
          }
        });
      });

      // then for each media line, follow the innerOrder
      session.media.forEach(function(mLine) {
        sdp.push(makeLine('m', grammar.m[0], mLine));

        innerOrder.forEach(function(type) {
          grammar[type].forEach(function(obj) {
            if (obj.name in mLine) {
              sdp.push(makeLine(type, obj, mLine));
            } else if (obj.push in mLine) {
              mLine[obj.push].forEach(function(el) {
                sdp.push(makeLine(type, obj, el));
              });
            }
          });
        });
      });

      return sdp.join('\r\n') + '\r\n';
    };

  }, {
    "./grammar": 2
  }]
}, {}, [1]);
;
/**
 * Event dispatcher that facilitates binding, unbinding and triggering of events.
 * @version: 0.0.2
 */

var Vent = function() {
  this.events = {};
  this.allEvents = {};
};

(function() {
  function formatEvents(events) {
    if (events instanceof Array) {
      array = events;
    } else if (events === undefined) {
      array = [];
    } else {
      array = [events];
    }
    return array;
  }

  function addEvent(listenerList, eventList, callback, context) {
    for (var i = 0; i < eventList.length; i++) {
      var event = eventList[i];

      if (!listenerList[event]) {
        listenerList[event] = [];
      }

      listenerList[event].push({
        context: context,
        callback: callback
      });
    }
    return listenerList;
  }

  function removeEvent(listenerList, eventList, callback, context) {
    var checkCallback = typeof callback === 'function',
      checkContext = typeof context === 'object' && context !== null;

    //no arguments - remove all events.
    if (eventList.length === 0) {
      listenerList = {};
    } else {
      for (var i = 0; i < eventList.length; i++) {
        var event = eventList[i],
          listeners = listenerList[event];

        if (listeners) {
          //don't need to bother with looping if we don't care about callback or context.
          if (!checkCallback) {
            delete listenerList[event];
          } else {
            for (var j = listeners.length - 1; j >= 0; j--) {
              var listener = listeners[j];

              if (listener.callback === callback) {
                if (checkContext) {
                  if (listener.context === context) {
                    listeners.splice(j, 1);
                  }
                } else {
                  listeners.splice(j, 1);
                }
              }
            }

            //cleanup events object if all listeners have been removed.
            if (listeners.length === 0) {
              delete listenerList[event];
            }
          }
        }
      }
    }

    return listenerList;
  }

  function triggerListeners(listeners, args, eventName) {
    var ListenersLen;
    for (var j = 0, ListenersLen = listeners.length; j < ListenersLen; j++) {
      var listener = listeners[j];
      var context = listener.context || {};
      context.eventName = eventName;
      try {
        listener.callback.apply(context, args);
      } catch (error) {
        Rtcc._safelog("Error in callback");
        Rtcc._safelog(error.stack);
      }
    }
  }



  Vent.prototype = {
    /**
     * Binds event listener(s).
     * @method on
     * @param events {string} space-separated list of event names.
     * @param callback {function} function to be invoked when event is triggered.
     * @param [context] {object} context to be passed to callback.
     * @return {object} this.
     */
    on: function(events, callback, context) {
      this.events = addEvent(this.events, formatEvents(events), callback, context);
      return this;
    },

    onAll: function(callback, context) {
      this.allEvents = addEvent(this.allEvents, ['all'], callback, context);
      return this;
    },

    /**
     * Unbinds event listener(s).
     * @method off
     * @param [events] {string} space-separated list of event names.
     * @param [callback] {function} function to compare with callback.
     * @param [context] {object} object to compare with context.
     * @return {object} this.
     */
    off: function(events, callback, context) {
      this.events = removeEvent(this.events, formatEvents(events), callback, context);
      return this;
    },
    offAll: function(callback, context) {
      this.allEvents = removeEvent(this.allEvents, ['all'], callback, context);
      return this;
    },



    /**
     * Triggers event listener(s).
     * @method trigger
     * @param events {string} space-separated list of event names.
     * @return {object} this.
     */
    trigger: function(eventList) {
      eventList = formatEvents(eventList);
      //convert arguments to an array.
      var args = Array.prototype.slice.call(arguments).slice(1);

      for (var i = 0; i < eventList.length; i++) {
        var listeners = this.events[eventList[i]];
        if (listeners) triggerListeners(listeners, args, eventList[i]);
        var allListeners = this.allEvents['all'];
        if (allListeners) triggerListeners(allListeners, args, eventList[i]);
      }
      return this;
    }
  };

})();



Vent.prototype.once = function(args) {
  var array,
    vent = this,
    callbacks = [];
  if (args instanceof Array) {
    array = args;
  } else {
    array = [args];
  }


  var factory_remove_all_and_fire = function(current) {
    return function() {
      if (array[current].action) {

        array[current].action.apply(this, arguments);
      }
      remove_all();
    };
  };

  var remove_all = function() {
    for (var i = 0; i < array.length; i++) {
      vent.off(array[i].event, callbacks[i]);
    }

  };

  for (var i = 0; i < array.length; i++) {
    callbacks.push(factory_remove_all_and_fire(i));
    this.on(array[i].event, callbacks[i]);
  }
};
;
var modeFacade = {};
var weemo = this;
var vent = new Vent();
;
var driverFacade = {};
;
var webrtcFacade = {};
;
var webrtcCall = {}
;
driverFacade.call = function(callId, direction, displayName, config) {
  this.dn = displayName;
  this.direction = direction;
  this.callId = callId;
  this.status = {
    call: null,
    video_remote: 'start',
    video_local: 'start',
    sound: null,
    record: "stop"
  };
  this.videoProfile = globalVars.videoProfile;
  this.terminated = false;
  var webRtcUi = globalVars.webRtcUi;
  var frameSizeDetectionEnabled = false;
  var framesize;

  var controlCall = function(id, item, action, appId) {
    if (appId) {
      action += "<appid>" + appId + "</appid>";
    }
    modeFacade.send("<controlcall id='" + id + "'><" + item + ">" + action + "</" + item + "></controlcall>");
  };

  var confControl = function(controlName, controlParameter) {
    var controlParameterStr = "";
    if (controlParameter) {
      controlParameterStr = "<p>" + controlParameter + "</p>"
    }
    modeFacade.send('<controlcall id="' + callId + '"><conference>' + controlName + controlParameterStr + '</conference></controlcall>');
  };

  var callEvents = new Vent();
  bindObjectToVent(this, callEvents)

  this.getDirection = function() {
    if (direction === "out") {
      return "outgoing";
    } else {
      return "incoming";
    }
  };

  this.lockActiveSpeaker = function(pid) {
    confControl.call(this, "lockas", pid);
  }

  this.unlockActiveSpeaker = function() {
    confControl.call(this, "unlockas");
  }

  this.turnOffActiveSpeaker = function() {
    confControl.call(this, "turnoffas");
  }

  this.sendInbandMessage = function(message) {
    modeFacade.send('<sendinband>' + message.encodeHTML() + '</sendinband>');
  }

  this.turnOnActiveSpeaker = function() {
    modeFacade.send('<controlcall id="' + this.callId + '"><conference>turnonas</conference></controlcall>')
  }

  this.setWindowSize = function(mode) {
    modeFacade.send("<controlcall id='" + this.callId + "'><windowsize>" + mode + "</windowsize></controlcall>");
  };

  this.callPointer = function(mode) {
    modeFacade.send("<controlcall id='" + this.callId + "'><callpointer mode='" + mode + "'></callpointer></controlcall>");
  };

  this.clearCallPointer = function() {
    modeFacade.send("<controlcall id='" + this.callId + "'><callpointer>clear</callpointer></controlcall>");
  };
  this.sharePointer = function(mode) {
    modeFacade.send("<controlcall id='" + this.callId + "'><sharepointer mode='" + mode + "'></sharepointer></controlcall>");
  };

  this._updateVideoProfile = function(profile) {
    var driverProfile;
    if (profile === this.videoProfile.THUMBNAIL || profile === this.videoProfile.SMALL) {
      driverProfile = 1;
    } else {
      driverProfile = 2;
    }
    modeFacade.send('<set videoprofile="' + driverProfile + '"/>');
  };

  this.dropAllAttendees = function() {
    weemo.requests.run('drop_all_attendees', [this]);
  };

  this.confControl = {
    kick: function(participantId) {
      confControl('drop', participantId);
    },
    mute: function(participantId) {
      confControl('mute', participantId);
    },
    unmute: function(participantId) {
      confControl('unmute', participantId);
    },
    deafen: function(participantId) {
      confControl('deafen', participantId);
    },
    undeafen: function(participantId) {
      confControl('undeafen', participantId);
    },
    muteAll: function() {
      confControl('muteall')
    },
    unmuteAll: function() {
      confControl('unmute');
    },
    deafenAll: function() {
      confControl('deafen');
    },
    undeafenAll: function() {
      confControl('undeafen');
    },
    lock: function() {
      confControl('lock');
    },
    unlock: function() {
      confControl('unlock');
    },
    shareSendRequest: function() {
      confControl('sharesendrequest');
    },
    shareLockRelease: function() {
        confControl('sharelockrelease');
      }
      // ,
      // recordStart: function(streams, url) {
      //   confControl('recordingstart', [streams, url]);
      // },
      // recordStop: function() {
      //   confControl('recordingstop', []);
      // },
      // recordPause: function() {
      //   confControl('recordingpause', []);
      // },
      // recordResume: function() {
      //   confControl('recordingresume', []);
      // },
      // recordBookmark: function() {
      //   confControl('recordingbookmark', []);
      // }
  };

  this.clearSharePointer = function() {
    modeFacade.send("<controlcall id='" + this.callId + "'><sharepointer>clear</sharepointer></controlcall>");
  };

  this.accept = function() {
    controlCall(this.callId, "call", "start");
  };

  this.updateVideoProfile = function(profile) {
    controlCall(this.callId, "video_remote", profile);
  };

  this.acceptNoVideo = function() {
    controlCall(this.callId, "call", "start_novideo");
  };


  this.hangup = function() {
    if (!this.terminated) {
      controlCall(this.callId, "call", "stop");
      if (config.plugin) webRtcUi.hangup();
    }
  };

  this.recordPause = function() {
    controlCall(this.callId, "record", "pause");
  };
  this.recordResume = function() {
    controlCall(this.callId, "record", "resume");
  };
  this.recordBookmark = function() {
    controlCall(this.callId, "record", "bookmark");
  };
  this.recordStop = function() {
    controlCall(this.callId, "record", "stop");
  };

  this.recordStart = function(url, mode) {
    var mode_str = "";
    if (mode) {
      mode_str = "mode='" + mode + "'";
    }
    modeFacade.send("<controlcall id='" + this.callId + "' url='" + url + "' " + mode_str + "><record>start</record></controlcall>");
  };


  this.videoStart = function() {
    controlCall(this.callId, "video_local", "start");
    if (config.plugin) {
      webRtcUi.enableLocalVideo();
    }
  };

  this.videoStop = function() {
    controlCall(this.callId, "video_local", "stop");
    if (config.plugin) {
      webRtcUi.disableLocalVideo();
    }
  };


  this.shareSave = function() {
    controlCall(this.callId, "share_remote", "save");
  };

  this.audioMute = function() {
    controlCall(this.callId, "sound", "mute");
    if (config.plugin) {
      webRtcUi.audioMute();
    }
  };

  this.audioUnMute = function() {
    controlCall(this.callId, "sound", "unmute");
    if (config.plugin) {
      webRtcUi.audioUnMute();
    }
  };



  this.settings = function() {
    controlCall(this.callId, "settings", "show");
  };


  this.shareStart = function(appId) {
    controlCall(this.callId, "share_local", "start", appId);
  };

  this.shareList = function() {
    controlCall(this.callId, "share_local", "list");
  };

  this.shareStop = function() {
    controlCall(this.callId, "share_local", "stop");
  };

  this.pip = function() {
    controlCall(this.callId, "pip", "show");
    if (config.plugin) {
      webRtcUi.pip();
    }
  };


  this.noPip = function() {
    controlCall(this.callId, "pip", "hide");
    if (config.plugin) {
      webRtcUi.noPip();
    }
  };

  this.enableFrameSizeDetection = function() {
    frameSizeDetectionEnabled = true;
    if (framesize) callEvents.trigger('video.framesize', framesize)
  }


  this._updateCallStatus = function(params) {
    switch (params.type) {
      case "datachannel":
        if (params.status === "ok") {
          callEvents.trigger('inband.message.ready');
        }
        break;
      case "call":
        if (params.sipCallId) {
          this.sipCallId = params.sipCallId;
        }
        this.status.call = params.status;
        if (params.status === "terminated") {
          this.status.reason = params.reason;
          if (config.plugin) webRtcUi.hangup();
        } else if (params.status === "active") {
          if (config.plugin) webRtcUi.acceptCall();
        }

        callEvents.trigger(statusCallEventName(this.status.call), this.status);
        break;
      case "frame_size":
        if (frameSizeDetectionEnabled)
          callEvents.trigger('video.framesize', {
            width: params.width,
            height: params.height
          });
        else
          framesize = {
            width: params.width,
            height: params.height
          }
        break;
      case "video_local":
        this.status.video_local = params.status;
        callEvents.trigger('video.local.' + params.status);
        break;

      case "video_remote":
        this.status.video_remote = params.status;
        callEvents.trigger('video.remote.' + params.status);
        break;

      case "sound":
        this.status.sound = params.status;
        callEvents.trigger('sound.' + params.status);
        break;
      case "record":
        this.status.record = params.status;
        callEvents.trigger('record.' + params.status, params.filename);
        break;
      case "share_local":
        callEvents.trigger('share.local.' + params.status);
        break;
      case "share_remote":
        callEvents.trigger('share.remote.' + params.status);
        break;
    }

    var arg;
    if (params.conference && params.conference.participantsStatus) {
      callEvents.trigger('conference.status', params.conference.participantsStatus);
    }
    if (params.conference && params.conference.participantList) {
      arg = {
        type: 'participant_list',
        status: params.conference.participantList
      }
      callEvents.trigger('conference.participants', params.conference.participantList)
    } else if (params.conference && params.conference.floor) {
      arg = {
        type: 'participant_order',
        status: params.conference.floor
      }
      callEvents.trigger('conference.participants.order', params.conference.floor)
    } else {
      arg = {
        type: params.type,
        status: params.status
      };
    }

    if (params.reason) {
      arg.reason = params.reason;
    }

    run_client_callback(weemo, 'onCallHandler', [this, arg]);

  };

};
;
driverFacade.connect = function() {
  var useSockets = global_config.useSockets;
  if (useSockets === true) {
    var uri = global_config.wdUri || global_config.wsUri;

    create_socket_connection.call(this, uri, global_config.protocol);
  } else {
    create_longpull_connection.call(this);
  }
};
;
driverFacade.getConnectionMode = function() {
  return Rtcc.connectionModes.DRIVER;
};
;
driverFacade.open = function() {
  modeFacade = driverFacade;
  setDriverRequests();
  setDriverConfig();
  sendConnectDriver();
}
;
var sendMessagePolling = function(message) {
  var messageTimeout = global_config.messageTimeout;
  var longpollUri = global_config.longpollUri;
  var xdr = new_cross_domain_request();
  window.jQuerySendMessage = function(obj) {
    debug("jquerySendMessage");
    debug(obj.x);
  };
  var script = document.createElement("script");
  var uri = encodeURIComponent(longpollId + ':' + message);
  var ts = (new Date().getTime() / 1000);
  debug("send_message_lognpull");
  var url = longpollUri + '?callback=jQuerySendMessage&command=' + uri + '&_=' + ts;
  script.async = true;

  script.src = url;

  // Attach handlers for all browsers
  script.onload = script.onreadystatechange = function(_, isAbort) {
    if (isAbort || !script.readyState || /loaded|complete/.test(script.readyState)) {

      // Handle memory leak in IE
      script.onload = script.onreadystatechange = null;

      // Remove the script
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }

      // Dereference the script
      script = null;
    }
  };
  // Circumvent IE6 bugs with base elements (#2709 and #4378) by prepending
  // Use native DOM manipulation to avoid our domManip AJAX trickery
  var head = document.head || document.getElementsByTagName('head')[0];
  // http://stackoverflow.com/questions/17100246/document-head-appendchildelement-ie-ie7-and-ie8
  head.insertBefore(script, head.firstChild);
};


var create_longpull_connection = function(config) {
  config = config || {};
  polling.call(this, config);
};



var longpollId;
var timeoutid;
var polling = function() {
  debug("polling started: first function");

  if (longpollId === undefined) {
    longpollId = uniqid();
  }
  var send_proxy_closed_late_if_necesary = function(data) {
    var pos = strpos(data.x, ":");
    var x = data.x.substring(pos + 1);
    var xmlDoc, readyforconnectionNode;
    debug(polling.is_connected);
    if (polling.is_connected === true) {
      xmlDoc = new XmlDoc(x);
      readyforconnectionNode = xmlDoc.getElementsByTagName("readyforconnection")[0];
      if (readyforconnectionNode !== undefined && readyforconnectionNode !== null) {
        debug('proxy closed earlier');
        polling.is_connected = false;
        triggerFacadeProxyClosed();
        return true;
      }
    } else {
      xmlDoc = new XmlDoc(x);
      readyforconnectionNode = xmlDoc.getElementsByTagName("readyforconnection")[0];
    }
    return false;
  };
  var useJquery = global_config.useJquery;
  var longpollUri = global_config.longpollUri;
  var pollingTimeout = global_config.pollingTimeout;
  var that = this;
  var pull_timeout = function() {
    setTimeout(function() {
      polling.call(that);
    }, 2000);
  };
  var uri = encodeURIComponent(longpollId + ':<poll></poll>');
  var ts = (new Date().getTime() / 1000);
  var unique_id = new Date().getTime();
  var url = longpollUri + '/?callback=jQueryPolling_' + unique_id + '&command=' + uri + '&_=' + ts;

  window['jQueryPolling_' + unique_id] = function(obj) {
    clearTimeout(timeoutid);
    var closing = send_proxy_closed_late_if_necesary(obj);

    if (!closing) {
      var data = obj;
      if (data !== "" && data !== undefined) {
        var pos = strpos(data.x, ":");
        if (pos !== false) {
          var responseId = data.x.substring(0, pos);
          if (responseId == longpollId) {
            data.x = data.x.substring(pos + 1);
            var value = data.x;
            polling.call(that);
            if (polling.is_connected !== true) {
              vent.trigger('facade_proxy_opened');
              polling.is_connected = true;
            }
            if (weemo.responseManager.handle(value) !== true) {
              debug(value + "not handled");
            }

            //pull_timeout();

          } else {
            debug("polling stoped, response id does not match request_id");
          }
        } else {
          debug("pos is false");
        }
      }

    }

    /*
      http://stackoverflow.com/questions/1073414/deleting-a-window-property-in-ie
     */
    try {
      delete window['jQueryPolling_' + unique_id];
    } catch (e) {
      window['jQueryPolling_' + unique_id] = undefined;
    }
  };
  if (true) {
    debug("polling started: adding script tag:" + unique_id);
    timeoutid = setTimeout(function() {
      debug('########################');
      debug('Timeout (polling) !');
      debug('########################');
      polling.is_connected = false;
      triggerFacadeProxyClosed();
    }, pollingTimeout);

    var script = document.createElement("script");
    script.async = true;


    script.src = url;

    // Attach handlers for all browsers
    script.onload = script.onreadystatechange = function(_, isAbort) {
      if (isAbort || !script.readyState || /loaded|complete/.test(script.readyState)) {

        // Handle memory leak in IE
        script.onload = script.onreadystatechange = null;

        // Remove the script
        if (script.parentNode) {
          script.parentNode.removeChild(script);
        }

        // Dereference the script
        script = null;

        // Callback if not abort
      }
    };
    /*
     * http://stackoverflow.com/questions/17100246/document-head-appendchildelement-ie-ie7-and-ie8
     */
    var head = document.head || document.getElementsByTagName('head')[0];
    head.insertBefore(script, head.firstChild);
  }
};
;
driverFacade.send = function(message, debug_options) {
  message = message || "";
  debug_options = debug_options || {};

  if (!global_config.useSockets) {
    sendMessagePolling(message);
  } else {
    if (this.websock) {
      debug_options.header = "BROWSER >>>> SOCKET (DRIVER)";
      this.websock.send(message);
      debug(message, debug_options);
    } else {
      throw 'websocket does not exist and was requested';
    }
  }
};
;
var socket_on_closing_check = function(socket, on_close_calback) {
  var run = function() {
    if (socket.readyState === WebSocket.CLOSING || socket.readyState === WebSocket.CLOSED) {
      clearInterval(interval_id);
      on_close_calback();
    }
  };

  var interval_id = setInterval(run, global_config.interval_to_check_socket_closed);
};

var create_socket_connection = function(url, protocol) {
  var browser = global_config.browser;

  try {

    if (this.websock) {
      this.websock.onopen = null;
      this.websock.onclose = null;
      this.websock.onmessage = null;
      this.websock.onerror = null;
      this.websock = null;
    }


    if (protocol) { // this implicitly means we are using the driver.
      this.websock = new WebSocket(url, protocol);
      this.websock.onopen = function() {
        vent.trigger('facade_proxy_opened');
      };
    } else {
      this.websock = new WebSocket(url);
      var disconnectOnNoResponse;
      var that = this;
      this.websock.onopen = function() {
        vent.trigger('facade_proxy_opened');
        disconnectOnNoResponse = new DisconnectOnNoResponse(that);
      };
    }

    socket_on_closing_check(this.websock, function() {
      debug("BROWSER >>>>> SOCKET IS CLOSE");
      if (disconnectOnNoResponse) {
        disconnectOnNoResponse.clean();
      }
      triggerFacadeProxyClosed();
    });



    this.websock.onmessage = function(evt) {
      if (weemo.responseManager.handle(evt.data) === true) {
        return;
      } else {
        debug(evt.data + "not handled");
      }
    };

    this.websock.onerror = function(error) {
      debug("BROWSER >>>>> SOCKET ERROR");
      debug(error);
    };
  } catch (exception) {
    debug("BROWSER >>>>> SOCKET EXCEPTION");
    debug(exception);
  }
};
;
var loadUi = function(callback) {
  var callbackWithUi = function() {
    if (!globalVars.webRtcUi) createUi();
    if (callback) callback();
  };

  if (typeof RtccUi !== 'object') {
    var min = global_config.debugLevel >= 1 ? '' : '.min';
    var uiUrl = global_config.uiVersion ? 'https://static.rtccloud.net/ui/' + global_config.uiVersion + '/RtccUi.js' : global_config.uiUrl;
    load_script(uiUrl, callbackWithUi);
  } else {
    callbackWithUi();
  }
};

var createUi = function() {
  globalVars.webRtcUi = new RtccUi.WebRtcUi(global_config, weemo);
  run_client_callback(weemo, 'onGetHandler', ["uiLoaded", 0]);
  apiEvents.trigger('ui.ready');
};
;
function setDriverRequests() {
  weemo.requests.name = "RtccDriver";
  weemo.requests.setRequests(driver_requests);
  weemo.responseManager.setParsers(driver_parsers);
  globalVars.state = Rtcc.STATES.CONNECTED_TO_FACADE;
}

function setDriverConfig() {
  weemo.setJsApiVersionToDriver();
  weemo.setUrlReferer(window.location.href);
  weemo.requests.run("set_user_agent");
}

function sendConnectDriver() {
  var hap = global_config.hap || '';
  modeFacade.send("<connect hap='" + hap + "'></connect>");
}
;
webrtcFacade.call = function(callid, params, displayName, config) {
  //defaults
  var that = this;
  that.isConference = params[5] || config.defaultCallIsConf;
  var log = webrtcCall.helper.log

  //state managers, to wait for all conditions before triggering a function
  var callActiveManager = new StateManager(['callActiveReceived', 'iceConnected'], onCallActive, true)
  var updatePListManager = new StateManager(['pListReceived', 'callActive']);
  var frameSizeDetectionManager = new StateManager(['startDetection', 'callActive'], startFrameSizeDetection);

  //feature objects
  var callEvents = new Vent();
  bindObjectToVent(this, callEvents);
  var videoConfig = new webrtcCall.VideoConfig(that.isConference)
  var connection = new webrtcCall.Connection(callEvents, params[3] /* startupRemoteDescription */ )
  var conference = that.isConference ? new webrtcCall.Conference(connection, videoConfig) : false;
  var videoDirection = new webrtcCall.VideoDirection(this, callEvents, connection, globalVars.webRtcUi)
  var iceCandidateManager = new webrtcCall.IceCandidateManager(connection, videoDirection, controlCallStart, sendUpdateMedia)
  var inbandChannel = new webrtcCall.InbandChannel(callEvents);
  var screenShare = new webrtcCall.ScreenShare(callEvents, connection, getUserMediaCallback, onLocalDescription, inbandChannel)
  var tabCapture = new webrtcCall.TabCapture(callEvents, connection, onLocalDescription)
  var webRtcUi = globalVars.webRtcUi;
  var frameSizeDetection;
  var stats;

  //non documented public
  this.sipCallId = params[4];
  this.callId = callid;
  this.dn = displayName;

  //documented attribute
  that.videoProfile = videoConfig.profiles;

  this.getConnection = function() {
    return connection;
  }

  this.getDirection = connection.getCallDirection

  this.settings = function() {
    debug('Not available in webRTC');
    run_client_callback(weemo, 'onCallHandler', ['notUseInThisMode', null]);
    callEvents.trigger('error.unavailable', 'settings');
  };

  this.enableFrameSizeDetection = function() {
    if (!frameSizeDetection)
      frameSizeDetectionManager.reach('startDetection').tryRun();
  }

  function startFrameSizeDetection() {
    frameSizeDetection = new callVideoFrameSize(
      connection.peer.getStats.bind(connection.peer),
      callEvents,
      connection
    )
  }

  this.audioMute = function() {
    connection.peer.getLocalStreams()[0].getAudioTracks()[0].enabled = false;
    connection.status.sound = "mute";
    //trigger mute event
    webRtcUi.audioMute();
    run_client_callback(weemo, 'onCallHandler', [this, {
      type: "sound",
      status: connection.status.sound
    }]);
    callEvents.trigger('sound.mute');
  }

  this.audioUnMute = function() {
    connection.peer.getLocalStreams()[0].getAudioTracks()[0].enabled = true;
    connection.status.sound = "unmute";
    //trigger unmute event
    webRtcUi.audioUnMute();
    run_client_callback(weemo, 'onCallHandler', [this, {
      type: "sound",
      status: connection.status.sound
    }]);
    callEvents.trigger('sound.unmute');
  }

  this.pip = webRtcUi.pip
  this.noPip = webRtcUi.noPip

  this.updateVideoProfile = function(profile) {
    var msg = {
      cmd: "updatevideoprofile",
      args: [that.callId, profile]
    };
    modeFacade.send(msg);
  }

  this.clean = function() {
    clean_finished_call();
    if (frameSizeDetection) frameSizeDetection.destroy();
  };

  this.hangup = function() {
    msg = {
      cmd: "controlcall",
      args: [that.callId, "stop"]
    };
    modeFacade.send(msg);
  }

  this._updateCallStatus = function(params) {
    switch (params.type) {
      case "active":
        callActiveManager.reach('callActiveReceived').tryRun();
        break;
      case "terminated":
        run_client_callback(weemo, 'onCallHandler', [that, {
          type: "webRTCcall",
          status: 'terminated',
          reason: params.reason
        }]);
        callEvents.trigger('terminate', params.reason);
        this.clean();
        break;
      case "proceeding":
        run_client_callback(weemo, 'onCallHandler', [that, {
          type: "webRTCcall",
          status: "proceeding"
        }]);
        callEvents.trigger('proceeding');
        break;
    }
  }


  //TODO move in conference object
  var updateParticipantList = function(pList) {
    if (pList.participants.length === 1) {
      webRtcUi.disableRemoteVideo();
    } else {
      webRtcUi.enableRemoteVideo();
    }
    webRtcUi.setParticipantList(pList);
  }


  //TODO move in conference object
  this._updateParticipantList = function(pList) {
    updatePListManager.setCallback(updateParticipantList.bind(this, pList))
    updatePListManager.reach('pListReceived').tryRun();
    callEvents.trigger('conference.participants', pList)
  };

  this.sendInbandMessage = inbandChannel.send;

  this._updateMedia = function(args) {
    log('onUpdateMedia')
    if (args[1] == "full") {
      var remoteDescObj = new RTCSessionDescription(args[2]);
      // Sanitize SDP, just in case...
      remoteDescObj.sdp = webrtcCall.helper.sdpCleanup(remoteDescObj.sdp);
      log(remoteDescObj)

      var sdpManager = new webrtcCall.SdpManager(remoteDescObj.sdp)
        //TODO use conference and screenshare modules as arguments to the SdpManager
      var data = sdpManager.parseAsRemote({
        isConference: this.isConference,
        remoteSharingTrackId: screenShare.remoteTrackId,
        passiveSpeakers: conference.passiveSpeakers
      });
      screenShare.remoteTrackId = data.remoteSharingTrackId;
      conference.passiveSpeakers = data.passiveSpeakers;
      conference.activeSpeakerId = data.activeSpeakerId;

      if (that.isConference) {
        updatePassiveVideoSources();
      }

      connection.peer.setRemoteDescription(remoteDescObj,
        setRemoteDescriptionCallback,
        webrtcCall.helper.defaultErrorHandling
      );
    } else {
      var candidate = new RTCIceCandidate(args[2]);
      connection.peer.addIceCandidate(
        candidate,
        function() {
          log('addIceCandidate, success')
        },
        webrtcCall.helper.defaultErrorHandling);
    }
  };


  function errorCleanCall(err) {
    webrtcCall.helper.defaultErrorHandling(err);

    if (!connection.isOutgoing) {
      that.hangup();
    } else {
      clean_finished_call();
    }
  }


  this._updateVideoProfile = function(profile) {
    log('onUpdateVideoProfile')

    var constraint = videoConfig.getConstraints(profile);

    // Profiles are only handled in 1:1 calls so it is safe to use only the first (and only) video track.
    var localStream = connection.peer.getLocalStreams()[0];
    var videoTrack = localStream.getVideoTracks()[0];
    if (videoTrack) {
      videoTrack.stop();
      localStream.removeTrack(videoTrack);
      getUserMedia(constraint, getUserMediaCallback, webrtcCall.helper.defaultErrorHandling);
    }
  };



  //TODO move in conference object
  var confControl = function(controlName, controlParameters) {
    var msg = {
      cmd: "conferencecontrol",
      args: [that.callId, controlName].concat(controlParameters)
    };
    modeFacade.send(msg);
  };

  //TODO move in conference object
  this.confControl = {
    kick: function(participantId) {
      confControl('kick', [participantId]);
    },
    mute: function(participantId) {
      confControl('mute', [participantId]);
    },
    unmute: function(participantId) {
      confControl('unmute', [participantId]);
    },
    deafen: function(participantId) {
      confControl('deafen', [participantId]);
    },
    undeafen: function(participantId) {
      confControl('undeafen', [participantId]);
    },
    muteAll: function() {
      confControl('muteall', []);
    },
    unmuteAll: function() {
      confControl('unmuteall', []);
    },
    deafenAll: function() {
      confControl('deafenall', []);
    },
    undeafenAll: function() {
      confControl('undeafenall', []);
    },
    lock: function() {
      confControl('lock', []);
    },
    unlock: function() {
      confControl('unlock', []);
    },
    shareSendRequest: function() {
      confControl('sharesendrequest', []);
    },
    shareLockRelease: function() {
      confControl('sharelockrelease', []);
    },
    recordStart: function(streams, url) {
      confControl('recordingstart', [streams, url]);
    },
    recordStop: function() {
      confControl('recordingstop', []);
    },
    recordPause: function() {
      confControl('recordingpause', []);
    },
    recordResume: function() {
      confControl('recordingresume', []);
    },
    recordBookmark: function() {
      confControl('recordingbookmark', []);
    }
  };


  this.recordStart = this.confControl.recordStart
  this.recordStop = this.confControl.recordStop
  this.recordPause = this.confControl.recordPause
  this.recordResume = this.confControl.recordResume
  this.recordBookmark = this.confControl.recordBookmark


  function clean_finished_call() {
    if (stats) {
      stats.endCall();
    }

    if (connection.peer) {
      var localStream = connection.peer.getLocalStreams()[0];
      if (localStream) {
        var audioTracks = localStream.getAudioTracks();
        if (audioTracks[0]) {
          audioTracks[0].stop();
        }
        var videoTracks = localStream.getVideoTracks();
        for (var i = 0; i < videoTracks.length; i++) {
          if (videoTracks[i].id !== tabCapture.trackId)
            videoTracks[i].stop()
          else
            localStream.removeTrack(videoTracks[i])
        }
        localStream.stop();
      }

      try {
        connection.peer.close();
      } catch (e) {
        debug('Tried to close peer connection when it was already closed.');
      }
    }

    screenShare.destroy();
    webRtcUi.hangup();
  }

  function sendUpdateMedia(candidate) {
    var msg = {
      cmd: "updatemedia",
      args: [that.callId, "candidate", candidate]
    };
    modeFacade.send(msg);
  }

  function controlCallStart() {
    var msg = {
      cmd: "controlcall",
      args: [that.callId, 'start', connection.peer.localDescription]
    };
    modeFacade.send(msg);
  }

  function createPeerConnection() {
    // Create and configure a new PeerConnection
    var peerConnectionConfig = getPeerConnectionConfig(modeFacade.turn);

    connection.peer = new RTCPeerConnection(peerConnectionConfig, {
      mandatory: [{
        googIPv6: false
      }]
    });

    connection.peer.onicecandidate = iceCandidateManager.onIceCandidate;
    connection.peer.onaddstream = onAddStream;
    connection.peer.onremovestream = onRemoveStream;
    connection.peer.oniceconnectionstatechange = onIceConnectionStateChange;
    connection.peer.onsignalingstatechange = function() {
      debug('Signaling state changed to ' + connection.peer.signalingState)
    };

    if (connection.isOutgoing) {
      rtccDataChannel = connection.peer.createDataChannel("rtccDataChannel", {
        reliable: false
      });
      inbandChannel.setChannel(rtccDataChannel);
    } else {
      connection.peer.ondatachannel = function(event) {
        inbandChannel.setChannel(event.channel);
      };
    }
  }

  var start = function(config) {
    config = config || {};
    var video = config.video;
    if (config.video !== false) video = videoConfig.defaultVideoOptions;

    var constraints = {
      video: video,
      audio: true
    };
    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "rtccUserMediaRequest",
      status: constraints
    }]);
    callEvents.trigger('webrtc.mediarequest', constraints);

    createPeerConnection();

    if (connection.isOutgoing) {
      webRtcUi.ringing(that, true);
      run_client_callback(weemo, 'onCallHandler', [that, {
        type: "webRTCcall",
        status: "outgoing"
      }]);
      callEvents.trigger('outgoing');
    }

    getUserMedia(
      constraints,
      getUserMediaCallback,
      function(error) {
        run_client_callback(weemo, 'onCallHandler', [that, {
          type: "rtccUserMediaError",
          status: error
        }]);
        callEvents.trigger('error', error);
        callEvents.trigger('webrtc.mediarequest.error', error);
        errorCleanCall(error);
      }
    );
  };

  this.acceptNoVideo = function() {
    videoDirection.localWantToSendVideo = false;
    start({
      video: false
    });
  };

  this.accept = function() {
    start();
  };

  this.videoStart = function() {
    if (!videoDirection.localWantToSendVideo) {
      videoDirection.localWantToSendVideo = true;

      run_client_callback(weemo, 'onCallHandler', [this, {
        type: "video_local",
        status: videoDirection.getVideoLocalStatusText()
      }]);
      callEvents.trigger('video.local.start');

      var status = {
        video: true,
        audio: false
      };
      run_client_callback(weemo, 'onCallHandler', [that, {
        type: "rtccUserMediaRequest",
        status: status
      }]);
      callEvents.trigger('webrtc.mediarequest', status);

      getUserMedia({
          video: videoConfig.defaultVideoOptions,
          audio: false
        },
        getUserMediaCallback,
        errorCleanCall
      );

    } else {
      debug('video already started');
    }
  };

  this.videoStop = function() {
    if (videoDirection.localWantToSendVideo) {
      videoDirection.localWantToSendVideo = false;
      connection.stopTracks();
      if (stats) stats.videoStop()
        //event
      run_client_callback(weemo, 'onCallHandler', [this, {
        type: "video_local",
        status: videoDirection.getVideoLocalStatusText()
      }]);
      callEvents.trigger('video.local.stop');
      webRtcUi.disableLocalVideo();
    }

    connection.createOffer(onLocalDescription);
  };

  this.shareStart = screenShare.shareStart
  this.shareStop = screenShare.shareStop

  this.tabCaptureStart = tabCapture.start
  this.tabCaptureHold = tabCapture.hold

  function callIsAlreadyEstablished() {
    return (connection.peer.iceConnectionState === 'completed' || connection.peer.iceConnectionState === 'connected')
  }

  function setLocalDescriptionCallback() {
    if (callIsAlreadyEstablished()) {
      var desc = {
        "sdp": connection.peer.localDescription.sdp,
        "type": connection.peer.localDescription.type
      };

      var slidestrackId = screenShare.trackId || tabCapture.trackId;
      if (slidestrackId) {
        // Set slidestrack label
        var re1 = new RegExp(" " + slidestrackId, "g");
        var re2 = new RegExp(slidestrackId, "g");
        desc.sdp = desc.sdp.replace(re1, "slides slidestrack");
        desc.sdp = desc.sdp.replace(re2, "slidestrack");
      }

      var msg = {
        cmd: "updatemedia",
        args: [that.callId, "full", desc]
      };
      modeFacade.send(msg);
    }
  }

  function onLocalDescription(description) {
    log("onLocalDescription: " + description)

    // Ensure that the video direction is properly set in SDP offer
    var localDescSdpManager = new webrtcCall.SdpManager(description.sdp)
    if (description.type === 'offer') {
      //TODO Mathieu: check this is still necessary
      localDescSdpManager.setDirection(videoDirection.getDirection())
    }

    description.sdp = webrtcCall.helper.sdpCleanup(localDescSdpManager.getSdp());
    connection.peer.setLocalDescription(description, setLocalDescriptionCallback, webrtcCall.helper.defaultErrorHandling);
  }

  function setRemoteDescriptionCallback() {
    log("setRemoteDescription SUCCESS")

    var mediaVideo;
    if (connection.peer.remoteDescription) {
      var sdpObject = sdpParser.parseSDP(connection.peer.remoteDescription.sdp);
      mediaVideo = webrtcCall.helper.getSDPVideoMedia(sdpObject);
    }

    videoDirection.setMediaVideo(mediaVideo);

    if (connection.peer.remoteDescription.type === "offer") {
      connection.createAnswer(onLocalDescription);
      if (connection.callActive) {
        videoDirection.triggerEventsRemote(mediaVideo);
      }
    }
  }

  function triggerCallActiveEvents() {
    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "webRTCcall",
      status: connection.status.call
    }]);
    callEvents.trigger('active');

    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "sound",
      status: connection.status.sound
    }]);
    callEvents.trigger('sound.' + connection.status.sound);

    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "video_remote",
      status: videoDirection.getVideoRemoteStatusText()
    }]);
    callEvents.trigger('video.remote.' + videoDirection.getVideoRemoteStatusText());

    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "video_local",
      status: videoDirection.getVideoLocalStatusText()
    }]);
    callEvents.trigger('video.local.' + videoDirection.getVideoLocalStatusText());
  }

  function onCallActive() {
    for (var i = 0; i < iceCandidateManager.candidates.length; i++) {
      sendUpdateMedia(iceCandidateManager.candidates[i])
    }

    if (!connection.callActive) {
      stats = new WebRtcCallStats(connection.peer, that.callId, connection);

      webRtcUi.acceptCall(
        connection.getLocalStream(),
        connection.remoteStream,
        videoDirection.localWantToSendVideo,
        videoDirection.remoteWantToSendVideo
      );
      updatePassiveVideoSources();
      webRtcUi.setRemoteStream(connection.remoteStream);
    }

    connection.status.call = 'active';
    connection.callActive = true;

    //trigger events last!
    triggerCallActiveEvents()

    updatePListManager.reach('callActive').tryRun();
    frameSizeDetectionManager.reach('callActive').tryRun();
  }

  //TODO move in conference object
  function updatePassiveVideoSources() {
    if (that.isConference) {
      var arg = [];
      for (var i = 0; i < conference.passiveSpeakers.length; i++) {
        if (conference.passiveSpeakers[i].src) {
          arg[i] = {
            src: (conference.passiveSpeakers[i].videoDisabled ? false : conference.passiveSpeakers[i].src),
            displayName: conference.passiveSpeakers[i].dn
          };
        }
      }
      webRtcUi.setPassiveVideoBoxes(arg);
    }
  }

  //TODO this looks very weird, check if we can do better
  function safeAddIncommingStreamToStats(stream) {
    /*
     * the incoming stream can become available before or after call active:
     *  - if the stream is available before call active stats will not exist when we run this function. The constructor in onCallActive will add this stream instead
     *  - if the stream is available after call active, the constructor will add undefined, and this function will add the incoming stream id to the stats object.
     */
    if (stats) {
      stats.mainIncomingVideoStreamId = stream;
    }
  }

  function onIceConnectionStateChange(event) {
    debug("onIceConnectionState " + connection.peer.iceConnectionState);
    if (connection.peer.iceConnectionState === "completed" || connection.peer.iceConnectionState === "connected") {
      callActiveManager.reach('iceConnected').tryRun();
    }
  }

  function onAddStream(event) {
    log('OnAddStream')
    var stream = event.stream;
    var videoTrackArray = stream.getVideoTracks();

    function onAddTrack() {
      webRtcUi.setRemoteStream(stream);
    }

    if (stream.id === screenShare.remoteTrackId) {
      // webRtcUi.startRemoteScreenSharingStream(stream);

      debug("Adding incoming screen sharing stream");
      callEvents.trigger('share.remote.start', stream);
    }
    // 1:1 call
    else if (!that.isConference) {
      connection.remoteStream = stream;
      webRtcUi.setRemoteStream(stream);
      stream.onaddtrack = onAddTrack
      if (videoTrackArray.length > 0) {
        connection.mainIncomingVideoStreamId = videoTrackArray[0].id;
        safeAddIncommingStreamToStats(connection.mainIncomingVideoStreamId);
      }
    }
    // N:N call active speaker stream
    //TODO move in conference object
    else if (stream.id === conference.activeSpeakerId) {
      connection.remoteStream = stream;
      if (videoTrackArray.length > 0) {
        connection.mainIncomingVideoStreamId = videoTrackArray[0].id;
        safeAddIncommingStreamToStats(connection.mainIncomingVideoStreamId);
      }
      webRtcUi.setRemoteStream(stream);
      stream.onaddtrack = onAddTrack
    }
    // N:N call passive speaker stream
    //TODO move in conference object
    else {
      for (var i = 0; i < conference.passiveSpeakers.length; i++) {
        if (stream.id === conference.passiveSpeakers[i].id) {
          conference.passiveSpeakers[i].src = window.URL.createObjectURL(stream);
          break;
        }
      }
    }

    updatePassiveVideoSources();
  }

  function onRemoveStream(event) {
    var stream = event.stream;
    if (screenShare.remoteTrackId && stream.id === screenShare.remoteTrackId) {
      debug("Removing incoming screen sharing stream");
      callEvents.trigger('share.remote.stop');
    }
    if (stream.id != conference.activeSpeakerId) {
      updatePassiveVideoSources();
    }
  }

  function getUserMediaCallback(stream) {
    log("gotStream: \n" + stream)

    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "rtccUserMediaAccepted"
    }]);
    callEvents.trigger('webrtc.mediarequest.success');

    var localStream = connection.peer.getLocalStreams()[0];
    var videoTracks = stream.getVideoTracks();

    if (stream.getAudioTracks().length > 0) {
      // It is the main stream, store it
      connection.peer.addStream(stream);
      var videoTrackArray = stream.getVideoTracks();
      if (videoTrackArray.length > 0) {
        connection.mainOutgoingVideoStreamId = videoTrackArray[0].id;
      }
    } else if (localStream && videoTracks.length > 0) {
      if (videoTracks[0].label === 'Screen') {
        videoTracks[0].onended = that.shareStop;
        screenShare.trackId = videoTracks[0].id;
        callEvents.trigger('share.local.start');
      }
      // Add the video track to the already existing stream
      localStream.addTrack(videoTracks[0]);
    }

    if (conference && conference.waitThumbStream(stream, getUserMedia, getUserMediaCallback, errorCleanCall)) {
      return;
    }

    // Send SDP offer/answer if this call is starting
    if (!connection.isEstablished()) {
      connection.initiateSdpOffer(onLocalDescription, setRemoteDescriptionCallback);
    }

    // Send updated SDP offer if this call is already running
    if (connection.callActive) {
      // The only action possible here is startLocalVideo since video is the only media
      // that can be started/stopped during the call for now
      webRtcUi.setLocalStream(localStream);
      webRtcUi.enableLocalVideo();
      if (stats) {
        stats.videoStart();
      }

      connection.createOffer(onLocalDescription);
    }
  }


  if (!connection.isOutgoing) {
    msg = {
      cmd: "statuscall",
      args: [that.callId, "call", 'proceeding']
    };

    modeFacade.send(msg);
    webRtcUi.ringing(that, false);
    run_client_callback(weemo, 'onCallHandler', [that, {
      type: "webRTCcall",
      status: "incoming"
    }]);
  }

};
;
function WebRtcCallStats(peer_connection, callId, connection) {
  var timeoutId;
  var data;
  var video_on = 1;
  var video_off = 0;
  var has_sent_first_message = false;
  var numRuns = 0; //0th runfirst call report is sent after 1min 10
  this.mainOutgoingVideoStreamId = connection.mainOutgoingVideoStreamId;
  this.mainIncomingVideoStreamId = connection.mainIncomingVideoStreamId;

  function initialize_data() {
    data = {
      voutwidth: [],
      voutheight: [],
      voutrr: [],
      voutgrab: [],
      vinwidth: [],
      vinheight: [],
      vinrr: [],
      vinlp: "",
      vinjit: "",
      ainlp: "",
      inbw: [],
      outbw: [],
      aindp: "",
      video_on: video_on,
      video_off: video_off,
      sharing_out_on: 0,
      remote_candidate_type: false,
      sharing_out_off: 1
    };
  }

  function shouldSendCallReport(end_report) {
    if (numRuns === 7 || end_report) {
      numRuns = 1; //after first run, call reports sent with one minute intervals
      return true;
    } else {
      return false;
    }
  }

  this.endCall = function() {
    clearTimeout(timeoutId);
    run.call(this, {
      end_report: true
    });
  };


  this.videoStop = function() {
    video_on = 0;
    video_off = 1;
  };
  this.videoStart = function() {
    video_on = 1;
    video_off = 0;

  };

  function formatHeightWidth(widthArray, heightArray, cb) {
    var width = safeApply(widthArray, cb);
    var height = safeApply(heightArray, cb);
    if (width === false || height === false) {
      return "";
    } else {
      return width + "x" + height;
    }
  }

  function formatSingleValue(data, cb) {
    var value = safeApply(data, cb);
    if (value === false) {
      return "";
    } else {
      return value;
    }
  }

  function safeApply(data, functionToApply) {
    if (data.length === 0) {
      return false;
    } else {
      return functionToApply.apply(null, data);
    }
  }

  function prepare_for_send(data, callId, end_report) {
    function average(times) {
      if (times.length === 0) {
        return "";
      }
      var sum = times.reduce(function(a, b) {
        return a + b;
      }, 0);
      var avg = sum / times.length;
      return avg;
    }
    var type;
    if (end_report) {
      type = "end";
    } else if (has_sent_first_message === false) {
      type = "start";
      has_sent_first_message = true;
    } else {
      type = "update";
    }


    var args = [callId, type];

    var vout = [];
    vout.push(formatHeightWidth(data.voutwidth, data.voutheight, Math.min));
    vout.push(formatHeightWidth(data.voutwidth, data.voutheight, Math.max));
    args.push(vout);

    var voutrr = [];
    voutrr.push(formatSingleValue(data.voutrr, Math.min));
    voutrr.push(formatSingleValue(data.voutrr, Math.max));
    voutrr.push(average(data.voutrr));
    args.push(voutrr);

    var voutgrab = [];
    voutgrab.push(formatSingleValue(data.voutgrab, Math.min));
    voutgrab.push(formatSingleValue(data.voutgrab, Math.max));
    voutgrab.push(average(data.voutgrab));
    args.push(voutgrab);

    var vin = [];
    vin.push(formatHeightWidth(data.vinwidth, data.vinheight, Math.min));
    vin.push(formatHeightWidth(data.vinwidth, data.vinheight, Math.max));

    args.push(vin);


    var vinrr = [];
    vinrr.push(formatSingleValue(data.vinrr, Math.min));
    vinrr.push(formatSingleValue(data.vinrr, Math.max));
    vinrr.push(average(data.vinrr));
    args.push(vinrr);

    args.push(["", "", ""]); //[ "vinlp_min", "vinlp_max", "vinlp_avg" ]
    args.push(["", "", ""]); //[ "vinjit_min", "vinjit_max", "vinjit_avg" ]
    args.push(["", "", ""]); //[ "ainlp_min", "ainlp_max", "ainlp_avg" ]

    var inbw = [];
    inbw.push(formatSingleValue(data.inbw, Math.min));
    inbw.push(formatSingleValue(data.inbw, Math.max));
    inbw.push(average(data.inbw));
    args.push(inbw);

    var outbw = [];
    inbw.push(formatSingleValue(data.outbw, Math.min));
    inbw.push(formatSingleValue(data.outbw, Math.max));
    inbw.push(average(data.outbw));
    args.push(outbw);

    args.push(["", "", ""]); //[ "aindp_min", "aindp_max", "aindp_avg" ]

    args.push(data.video_on); // video on
    args.push(data.video_off);

    args.push(0); // 'sharing_out_on'
    args.push(1); // 'sharing_out_off'
    args.push(data.remote_candidate_type);

    //  , , ,, , "video_on", "video_off", "sharing_out_on", "sharing_out_off"
    return {
      "cmd": "callreport",
      "args": args
    };
  }

  var Bitrate = function() {
    var lastTime;
    var lastReceived = 0;
    this.calculate = function(audio, videoIn) {
      var video = videoIn || 0;
      var difference, timeDifference;
      var now = new Date();
      if (lastTime) {
        timeDifference = now - lastTime;
        difference = (audio + video) - lastReceived;
      }
      lastTime = now;
      lastReceived = (audio + video);

      return difference ? difference * 8 / timeDifference : false;
    };
  };
  var in_bitrate = new Bitrate();
  var out_bitrate = new Bitrate();

  function run(config) {
    config = config || {};
    var end_report = config.end_report || false;
    var that = this;
    numRuns++;
    peer_connection.getStats(function(stat) {
      var audioBitrateIn, videoBitrateIn, audioBitrateOut, videoBitrateOut;
      for (var i = 0; i < stat.result().length; i++) {

        if (stat.result()[i].type === "googCandidatePair") {
          if (stat.result()[i].stat("googActiveConnection") == "true") {
            var oldStatName = stat.result()[i].stat("googRemoteCandidateType");
            switch (oldStatName) {
              case 'local':
                data.remote_candidate_type = 'host';
                break;
              case 'stun':
                data.remote_candidate_type = 'serverreflexive';
                break;
              case 'relay':
                data.remote_candidate_type = 'relayed';
                break;
              default:
                data.remote_candidate_type = oldStatName;
                break;
            }

            //debug("Active connection: local=" + stat.result()[i].stat("googLocalAddress") + " - remote=" + stat.result()[i].stat("googRemoteAddress") +
            //" - " + stat.result()[i].stat("googLocalCandidateType") + "/" + stat.result()[i].stat("googTransportType"));
          }
        } else if (stat.result()[i].type === "ssrc") {
          if ((stat.result()[i].stat("googFrameHeightSent") !== '') && (that.mainOutgoingVideoStreamId === stat.result()[i].stat("googTrackId"))) {
            data.voutwidth.push(Number(stat.result()[i].stat("googFrameWidthSent")));
            data.voutheight.push(Number(stat.result()[i].stat("googFrameHeightSent")));
            data.voutrr.push(Number(stat.result()[i].stat("googFrameRateSent")));
            data.voutgrab.push(Number(stat.result()[i].stat("googFrameRateInput")));
            videoBitrateOut = Number(stat.result()[i].stat("bytesSent"));
          } else if ((stat.result()[i].stat("googFrameHeightReceived") !== '') && (that.mainIncomingVideoStreamId === stat.result()[i].stat("googTrackId"))) {
            data.vinwidth.push(Number(stat.result()[i].stat("googFrameWidthReceived")));
            data.vinheight.push(Number(stat.result()[i].stat("googFrameHeightReceived")));
            data.vinrr.push(Number(stat.result()[i].stat("googFrameRateReceived")));
            videoBitrateIn = Number(stat.result()[i].stat("bytesReceived"));
          } else if (stat.result()[i].stat("audioOutputLevel") !== '') {
            audioBitrateIn = Number(stat.result()[i].stat("bytesReceived"));
          } else if (stat.result()[i].stat("audioInputLevel") !== '') {
            audioBitrateOut = Number(stat.result()[i].stat("bytesSent"));
          }
        } else if (stat.result()[i].type === "VideoBwe") {
          debug("Outgoing video bandwidth: " + stat.result()[i].stat("googTransmitBitrate") + " bps", {
            show_on_debug_level: 2
          });
        }
      }


      var currentBitrateIn = in_bitrate.calculate(audioBitrateIn, videoBitrateIn);
      if (currentBitrateIn) {
        data.inbw.push(currentBitrateIn);

      }
      var currentBitrateOut = out_bitrate.calculate(audioBitrateOut, videoBitrateOut);
      if (currentBitrateOut) {
        data.outbw.push(currentBitrateOut);
        debug("Outgoing total bandwidth: " + currentBitrateOut + " bps", {
          show_on_debug_level: 2
        });

      }
      if (shouldSendCallReport(end_report)) {
        var converted_data = prepare_for_send(data, callId, end_report);
        modeFacade.send(converted_data, {
          show_on_debug_level: 2
        });
        initialize_data();
      }

      if (!end_report) {
        timeoutId = setTimeout(function() {
          run.call(that);
        }, 10000);
      }

    });

  }
  initialize_data();
  var that = this;
  timeoutId = setTimeout(function() {
    run.call(that);
  }, 10000);

  //var baselineReport, currentReport;



}
;
function callVideoFrameSize(getStats, callEvents, connection, delay) {
  delay = delay || 1000
  var framesize = {
    height: undefined,
    width: undefined
  };
  var fsWidth;
  var fsHeight;
  var timeoutId;

  function getStatWithSsrc(stat) {
    var typeSsrc = [];
    for (var i = 0; i < stat.result().length; i++) {
      if (stat.result()[i].type === "ssrc") {
        typeSsrc.push(stat.result()[i]);
      }
    }
    return typeSsrc;
  }

  function getVideoFrameSize(stat) {
    var ssrcList = getStatWithSsrc(stat);
    var newFrameSize = {}
    for (var i = 0; i < ssrcList.length; i++) {
      if (connection.mainIncomingVideoStreamId === ssrcList[i].stat("googTrackId") && ssrcList[i].stat("googFrameHeightReceived") !== '') {
        newFrameSize.width = Number(ssrcList[i].stat("googFrameWidthReceived"));
        newFrameSize.height = Number(ssrcList[i].stat("googFrameHeightReceived"));
      }
    }
    return newFrameSize
  }


  (function pollStat() {
    getStats(function(stats) {
      var newFrameSize = getVideoFrameSize(stats)
      if (
        newFrameSize.width != framesize.width ||
        newFrameSize.height != framesize.height
      ) {
        framesize = newFrameSize
          //we have to clone the object, because it's passed as a reference
        callEvents.trigger('video.framesize', clone(framesize))
      }
      timeoutid = setTimeout(pollStat, delay)
    })
  })()

  this.destroy = function() {
    clearTimeout(timeoutid)
  }
}
;
webrtcFacade.choose_realtime_platform = function(real_time_servers_info) {
  var tabWs = [],
    tabStart = [],
    tabCurrentRun = [],
    // 982, 146, 374, 450, 906, 70, 1362, 1058, 222, 526, 1210, 830, 754, 602, 1134, 298
    messages = [
      randomString(982),
      randomString(146),
      randomString(374),
      randomString(450),
      randomString(906),
      randomString(70),
      randomString(1362),
      randomString(1058),
      randomString(222),
      randomString(526),
      randomString(1210),
      randomString(830),
      randomString(754),
      randomString(602),
      randomString(1134),
      randomString(298)
    ],
    returned_data = {};
  returned_data.unreachable = [];

  function run() {
    returned_data.techdomain = real_time_servers_info.techdomain;
    returned_data.localAddress = real_time_servers_info.localAddress;
    var onMessageHandler = function(evt) {
      handleProbeData(evt.data, real_time_servers_info);
    };
    var onErrorHandler = function(error) {
      debug("SOCKET PROBE ERROR");
    };

    if (real_time_servers_info.tuntab.length > 0) {
      for (var j = 0; j < real_time_servers_info.tuntab.length; j++) {
        var ws = new WebSocket(global_config.probeProtocol + "://" + real_time_servers_info.tuntab[j].address + ':' + real_time_servers_info.tuntab[j].port);
        wrap_ws_open(ws, j);
        wrap_ws_close(ws, j);
        ws.onmessage = onMessageHandler;
        ws.onerror = onErrorHandler;
        tabWs.push(ws);

      }

    } else {
      throw 'no serversfound';
    }
  }


  function byteString(string, total_num_digits) {
    var bytes = string.length;
    var digits = String(bytes);
    var num_digits = digits.length;
    for (var i = num_digits; i < total_num_digits; i++) {
      digits = "0" + digits;
    }
    return digits;
  }

  function build_string_for_current_run(index) {
    var num_of_run = tabCurrentRun[index];
    var msg = messages[num_of_run];
    msg = String(index) + msg;
    return byteString(msg, 5) + ":" + msg;
  }


  function onCloseProbeTest(evt, index) {
    if ((evt.code === 1006) && (need_probe_success)) {
      returned_data.unreachable.push(evt.currentTarget.URL);
    }
    if ((returned_data.unreachable.length) === tabWs.length) {
      debug('Probes NOK');
      vent.trigger('probes_nok');
    }
  }

  function startProbeTest(k) {
    tabStart[k] = new Date().getTime();
    tabCurrentRun[k] = 0;
    tabWs[k].send(build_string_for_current_run(k));
  }
  var need_probe_success = true;

  function closeAllSockets() {
    for (var i = 0; i < tabWs.length; i++) {
      tabWs[i].close();
    }
  }

  function handleProbeData(data, server_info) {
    var index = Number(data.substring(6, 7));
    tabCurrentRun[index] += 1;
    if (tabCurrentRun[index] < messages.length) {
      tabWs[index].send(build_string_for_current_run(index));
    } else {
      var tabEnd = new Date().getTime();
      var tabTime = tabEnd - tabStart[index];
      need_probe_success = false;
      closeAllSockets();
      debug("--------------------------");
      latency = tabTime / messages.length;
      server = server_info.tuntab[index].address;

      var name = server_info.tuntab[index].name;
      returned_data.probe = {
        name: name,
        server: server,
        latency: latency,
        webrtc: server_info.tuntab[index].webrtc,
        turn: server_info.tuntab[index].turn,
        port: server_info.tuntab[index].port
      };
      vent.trigger('probes_ok', returned_data);

    }
  }

  function wrap_ws_open(ws, index) {
    ws.onopen = function(a, b) {
      startProbeTest(index);
    };
  }

  function wrap_ws_close(ws, index) {
    ws.onclose = function(evt) {
      onCloseProbeTest(evt, index);
    };
  }

  run();

};
;
webrtcFacade.connectWebRTC = function(url) {
  create_socket_connection.call(this, url, undefined);
};

var DisconnectOnNoResponse = function() {
  debug("DisconnectOnNoResponse init");
  var timeout = global_config.webp_timeout;
  var timebetweenpings = global_config.webp_timebetweenpings;
  var nextRun;
  var timeoutReached = function() {
    clearTimeout(nextRun);
    debug("DisconnectOnNoResponse timeoutReached");
    var callObjects = global_config.callObjects;
    objectForEach(callObjects, function(k, v) {
      if (typeof v.clean === 'function') v.clean();
    })
    webrtcFacade.websock.close();
  };
  this.clean = function() {
    clearTimeout(nextRun);
    clearTimeout(globalVars.timeout.disconnect_on_no_pong_timeoutid);
    vent.off("pong");

  };
  var run = function() {
    vent.off("pong");
    debug("DisconnectOnNoResponse run");

    vent.on("pong", function() {
      clearTimeout(globalVars.timeout.disconnect_on_no_pong_timeoutid);
      debug("DisconnectOnNoResponse clearTimeout");

      nextRun = setTimeout(run, timebetweenpings);
    });
    globalVars.timeout.disconnect_on_no_pong_timeoutid = setTimeout(timeoutReached, timeout);
    webrtcFacade.send({
      cmd: "ping",
      args: []
    }, {
      show_on_debug_level: 2
    });
  };
  run();
};
;
webrtcFacade.getConnectionMode = function() {
  return Rtcc.connectionModes.WEBRTC;
};
;
webrtcFacade.getHap = function() {
  var hap = global_config.hap;
  var xdr = new_ajax_request();
  var url = global_config.hap_url[global_config.current_hap] + "/" + hap;

  xdr.onload = function() {
    if (xdr.status === 200) {
      var hap_info = parseHapXml(xdr.responseText);
      vent.trigger('hap_ok', {
        hap: hap_info
      });
    } else {
      vent.trigger('hap_nok');
    }
  };
  xdr.onerror = function() {
    debug("ERROR TO GET HAP 1 FILE");
    vent.trigger('hap_nok');
  };
  xdr.ontimeout = function() {
    debug("TIMEOUT TO GET HAP 1 FILE");
    vent.trigger('hap_nok');
  };


  xdr.open("GET", url);
  xdr.timeout = 16000;
  xdr.send();
};
;
webrtcFacade.open = function() {
  modeFacade = webrtcFacade;
  weemo.requests.name = "WebRtc";
  weemo.requests.setRequests(webrtc_requests);
  weemo.responseManager.setParsers(webrtc_parsers);
  globalVars.state = Rtcc.STATES.CONNECTED_TO_FACADE;
  actions.authenticate(global_config);
};
;
webrtcFacade.send = function(msg, debug_options) {
  debug_options = debug_options || {};
  var stringified_msg = JSON.stringify(msg);
  webrtcFacade.websock.send(stringified_msg);
  debug_options.header = 'BROWSER >>>> SOCKET (WEBRTC)';
  debug(stringified_msg, debug_options);
};
;
webrtcCall.Conference = function(connection, videoConfig) {
  var that = this;

  that.activeSpeakerId = false;
  that.passiveSpeakers = [];

  var gotMainConfStream = false


  that.waitThumbStream = function(stream, getUserMedia, getUserMediaCallback, errorCleanCall) {
    if (!gotMainConfStream) {
      gotMainConfStream = true;
      // Get thumbnail stream
      if (stream.getVideoTracks().length > 0) {
        getUserMedia(
          videoConfig.constraintsThumb,
          getUserMediaCallback,
          errorCleanCall
        );
        return true;
      }
    }
    return false;
  }

}
;
webrtcCall.Connection = function(callEvents, startupRemoteDescription) {
  var that = this;
  that.peer = false;
  that.callActive = false
  that.startupRemoteDescription = startupRemoteDescription;
  that.isOutgoing = (startupRemoteDescription === '') //if no remote description at start, the call is outgoing
  that.remoteStream = false;
  that.mainOutgoingVideoStreamId = false;
  that.mainIncomingVideoStreamId = false;

  that.status = {
    call: null,
    sound: null
  };

  /* that.updateMedia = ...
  that.getUserMediaCallback = ...*/


  that.createAnswer = function(onLocalDescription) {
    that.peer.createAnswer(onLocalDescription, debug, {
      mandatory: {
        OfferToReceiveAudio: true,
        OfferToReceiveVideo: true
      }
    });
  }

  that.createOffer = function(onLocalDescription) {
    that.peer.createOffer(onLocalDescription, debug, {
      mandatory: {
        OfferToReceiveAudio: true,
        OfferToReceiveVideo: true
      }
    });
  }

  that.getLocalStream = function() {
    return that.peer.getLocalStreams()[0]
  }

  that.getCallDirection = function() {
    return that.isOutgoing ? "outgoing" : "incoming"
  }

  function descriptionHasSdp(desc) {
    return !!(desc && desc.sdp !== '') //boolean cast
  }

  that.isEstablished = function() {
    return descriptionHasSdp(that.peer.remoteDescription)
  }

  that.initiateSdpOffer = function(onLocalDescription, setRemoteDescriptionCallback) {
    if (that.startupRemoteDescription === '') {
      // It is the start of an outgoing call
      that.createOffer(onLocalDescription);
    } else {
      // It is the start of an incoming call
      that.peer.setRemoteDescription(new RTCSessionDescription(that.startupRemoteDescription),
        setRemoteDescriptionCallback,
        webrtcCall.helper.defaultErrorHandling
      );
    }
  }


  that.stopTracks = function() {
    var localStream = that.getLocalStream()
    var videoTracks = localStream.getVideoTracks();
    for (var i = 0; i < videoTracks.length; i++) {
      videoTracks[i].stop();
      localStream.removeTrack(videoTracks[i]);
    }
    gotMainConfStream = false;
  }

}
;
webrtcCall.IceCandidateManager = function(connection, videoDirection, sendSdp, updateMedia, options) {

  var that = this;
  options = options = {}
  options.iceTimeout = options.iceTimeout || 300
  that.sdpSent = false;
  that.candidates = [];

  var gotAudioCandidate = false;
  var gotVideoCandidate = false;
  var iceGatheringTimeout;


  function callStart() {
    that.sdpSent = true;
    sendSdp()
  }

  function handleCandidate(event) {
    if (!that.sdpSent) {
      //wait for all ice candidates before sending the SDP
      if (that.shouldSendSDP(event)) {
        clearTimeout(iceGatheringTimeout);
        //after a certain time without receiving cendidates, we send the SDP
        iceGatheringTimeout = setTimeout(callStart, options.iceTimeout);
      }
    } else {
      if (connection.callActive) {
        debug('updateMedia')
        updateMedia(event.candidate);
      } else {
        that.candidates.push(event.candidate);
      }
    }
  }

  function endOfCandidates() {
    if (!that.sdpSent) {
      clearTimeout(iceGatheringTimeout);
      callStart();
    }
  }

  that.onIceCandidate = function(event) {
    if (event.candidate) {
      debug("Local ICE candidate: \n" + event.candidate)
      handleCandidate(event)
    } else {
      debug("END OF CANDIDATES")
      endOfCandidates()
    }
  }


  that.shouldSendSDP = function(event) {
    if (event.candidate.sdpMid == "audio") {
      gotAudioCandidate = true;
    } else if (event.candidate.sdpMid == "video") {
      gotVideoCandidate = true;
    }
    return gotAudioCandidate && (!videoDirection.localWantToSendVideo || gotVideoCandidate)
  }


}
;
webrtcCall.InbandChannel = function(callEvents) {
  var that = this
  var channel;
  var extMode = false;
  var extChannel;

  that.setChannel = function(newChannel) {
    channel = newChannel;

    channel.onmessage = function(evt) {
      if (extMode) {
        extChannel(evt.data)
      } else {
        run_client_callback(weemo, 'onInbandMessageReceived', [evt.data]);
        apiEvents.trigger('message.inband', evt.data);
        callEvents.trigger('inband.message.receive', evt.data);
      }
    };

    channel.onopen = function() {
      callEvents.trigger('inband.message.ready');
    };
  }

  that.setScreenshareExtChannel = function(channelFunction) {
    extChannel = channelFunction
  }

  that.enableRedirectToExtension = function() {
    extMode = true;
  }
  that.disableRedirectToExtension = function() {
    extMode = false;
  }

  that.send = function(msg) {
    if (!channel || channel.readyState !== "open") {
      debug('cannot send message `' + msg + '`, inband message not established')
    } else {
      debug("sending inband message:" + msg);
      channel.send(msg);
    }
  }

}
;
webrtcCall.ScreenShare = function(callEvents, connection, getUserMediaCallback, onLocalDescription, channelInband) {
  var that = this
  that.trackId = false;
  that.remoteTrackId = false

  channelInband.setScreenshareExtChannel(forwardInbandToExt)

  function forwardInbandToExt(msg) {
    window.postMessage({
      type: "FROM_RTCC_PAGE",
      message: {
        type: "inband",
        value: msg
      }
    }, "*");
  }


  that.shareStart = function() {
    // Extension Detection
    if (!weemo.isShareExtensionLoaded()) {
      callEvents.trigger('chrome.screenshare.missing', globalVars.screenShareExtentionUrl);
      return;
    }
    // Trigger ChoseDesktopMedia in extension
    window.postMessage({
      type: "FROM_RTCC_PAGE",
      content: {
        type: "rtccChooseDesktopMedia",
        content: ""
      }
    }, "*");
  };


  that.shareStop = function() {
    var localStream = connection.getLocalStream();
    if (!localStream) {
      debug("shareStop: No localStream.");
      return;
    }

    var videoTracks = localStream.getVideoTracks();
    if (!videoTracks) {
      debug("shareStop: No Video Track");
      return;
    }

    var shareTracks = arrayFilter(videoTracks, function(v) {
      return v.label === 'Screen'
    })
    if (shareTracks.length === 0) {
      debug('shareStop: no share track')
      return
    }

    var track = shareTracks[0];
    if (track.readyState === "ended") {
      that.trackId = "";
      localStream.removeTrack(track);
      connection.createOffer(onLocalDescription);
      callEvents.trigger('share.local.stop');
    } else {
      track.stop(); // Will trigger the 'onended' callback
    }
  }

  function getUserMedia(sourceId) {
    navigator.getUserMedia({
        audio: false,
        video: {
          mandatory: {
            chromeMediaSource: "desktop",
            maxHeight: screen.height,
            maxWidth: screen.width,
            chromeMediaSourceId: sourceId,
            maxFrameRate: 4
          }
        }
      },
      getUserMediaCallback,
      debug);
  }

  function extensionEventHandler(event) {
    if (event.source != window)
      return
    if (event.data.type !== "FROM_RTCC_EXT")
      return

    var message = event.data.content;
    if (message.type === "rtccGotDesktopMedia") {
      if (!message.content) {
        debug("Desktop capture: Access denied");
        return
      }
      getUserMedia(message.content)
    } else if (message.type === "tabCaptureSdp") {
      channelInband.send('RTCCSDP' + message.value)
      channelInband.enableRedirectToExtension()
    } else if (message.type === 'tabCaptureStop') {
      channelInband.disableRedirectToExtension()
    }

  }

  that.destroy = function() {
    window.removeEventListener('message', extensionEventHandler);
  }

  // Sceenshare Extension interface
  window.addEventListener('message', extensionEventHandler);
}
;
webrtcCall.SdpManager = function(sdp) {
  'use strict'

  var that = this;

  that.getSdp = function() {
    return sdp
  }

  function getPassiveSpeaker(passiveSpeakerLines, ssrc, trackId, oldPassiveSpeakersList) {
    // Look for the pattern in the "invalid" lines (unrecognized by sdp-transform)
    // filter passive speakers with display name
    var withDisplayName = arrayFilter(passiveSpeakerLines, function(v) {
      return v.value.search("ssrc:" + ssrc.id + " x-display-name") != -1
    })

    function getFilter(id) {
      return function(v) {
        return id === v.id
      }
    }

    //get src
    var newSrc;
    var oldPassiveSpeaker = arrayFilter(oldPassiveSpeakersList, getFilter(trackId));
    //Will change for Firefox
    if (oldPassiveSpeaker[0]) newSrc = oldPassiveSpeaker[0].src;

    return {
      // Save the display name 
      dn: withDisplayName[0].value.split('"')[1],
      id: trackId,
      src: newSrc,
      // Handle disabled streams
      videoDisabled: (withDisplayName[0].value.search("x-disabled") !== -1)
    };
  }


  that.parseAsRemote = function(context) {
    var remoteSharingTrackId = context.remoteSharingTrackId || false;
    var activeSpeakerId = false;
    var newPassiveSpeakersList = [];
    var trackId, track_label;

    var videoMedia = webrtcCall.helper.getSDPVideoMedia(sdpParser.parseSDP(sdp))
    for (var i = 0; i < videoMedia.length; i++) {
      var ssrcsWithMsid = arrayFilter(videoMedia[i].ssrcs || [], function(v) {
        return v.attribute === 'msid'
      })
      for (var j = 0; j < ssrcsWithMsid.length; j++) {

        var ssrc = ssrcsWithMsid[j]
        trackId = ssrc.value.split(' ')[0];
        track_label = ssrc.value.split(' ')[1];

        // Screen sharing SSRC ?
        if (track_label === "slidestrack") {
          remoteSharingTrackId = trackId;
        } else if (context.isConference) {
          // Active speaker SSRC ?
          /*
          if (stream_label === "videotrack") {
            activeSpeakerId = stream_id;
          } else {
            // Parse passive speakers
            parsePassiveSpeakers(sdp, ssrc, tmp_newPassiveSpeakers);
          }
          */
          //TODO: Must be changed when the WebRTC-screenshare-compatible MVS is available (see commented code above)
          if (activeSpeakerId === false) {
            // Consider the first SSRC as the active speaker.
            activeSpeakerId = trackId;
          }
          // passive speakers are in the invalid lignes. SDP transform does not recognize it
          else if (videoMedia[i].invalid) {
            var newPassiveSpeaker = getPassiveSpeaker(videoMedia[i].invalid, ssrc, trackId, context.passiveSpeakers);
            newPassiveSpeakersList.push(newPassiveSpeaker)
          }
        }
      }
    }

    return {
      passiveSpeakers: newPassiveSpeakersList,
      activeSpeakerId: activeSpeakerId,
      remoteSharingTrackId: remoteSharingTrackId
    }
  }


  that.setDirection = function(newDirection) {
    // Find video m-line
    var sdpLines = sdp.split('\r\n');
    var mLineIndex = findLine(sdpLines, 'm=', 'video');

    if (mLineIndex) {
      // Find next m-line if any.
      var nextMLineIndex = findLineInRange(sdpLines, mLineIndex + 1, -1, 'm=') || sdpLines.length;

      // Find direction line between video m-line and next m-line.
      var directionLineIndex;
      objectForEach(webrtcCall.VideoDirection.directions, function(k, v) {
        if (!directionLineIndex)
          directionLineIndex = findLineInRange(sdpLines, mLineIndex + 1, nextMLineIndex, 'a=' + v);
      })

      if (directionLineIndex) {
        sdpLines[directionLineIndex] = 'a=' + newDirection;
        sdp = sdpLines.join('\r\n');
      }
    }
    return that
  }

  function findLine(sdpLines, prefix, substr) {
    return findLineInRange(sdpLines, 0, -1, prefix, substr);
  }

  function findLineInRange(sdpLines, startLine, endLine, prefix, substr) {
    var realEndLine = endLine !== -1 ? endLine : sdpLines.length;
    for (var i = startLine; i < realEndLine; ++i) {
      if (sdpLines[i].indexOf(prefix) === 0) {
        if (!substr || sdpLines[i].toLowerCase().indexOf(substr.toLowerCase()) !== -1) {
          return i;
        }
      }
    }
  }

}
;
webrtcCall.TabCapture = function(callEvents, connection, onLocalDescription) {

  var that = this;
  var log = webrtcCall.helper.log
  that.trackId = false;


  this.start = function(tabStream) {
    if (!tabStream) {
      log("tabCaptureStart: tab stream not found.")
      return
    }

    var videoTabTracks = tabStream.getVideoTracks();
    if (videoTabTracks.length === 0) {
      log("tabCaptureStart: Couldn't find a video track in the tab stream.")
      return
    }

    if (!connection.callActive) {
      log("tabCaptureStart: The call is not active.")
      return
    }

    var track = videoTabTracks[0]
    that.trackId = track.id;
    connection.getLocalStream().addTrack(track);
    connection.createOffer(onLocalDescription);
  }


  // Holds the tab stream without stopping it.
  this.hold = function() {
    if (!connection.callActive) {
      log("tabCaptureHold: The call is not active.")
      return
    }

    var localStream = connection.getLocalStream();
    if (localStream && that.trackId) {
      var tabCaptureTracks = arrayFilter(localStream.getVideoTracks(), function(v) {
        return v.id === that.trackId
      })
      if (tabCaptureTracks[0]) {
        that.trackId = "";
        // Stop track and update SDP offer
        localStream.removeTrack(tabCaptureTracks[0]);
        connection.createOffer(onLocalDescription);
      }
    }
  }

  //There is no stop function since we don't destroy the stream until the extension
  //popup is closed. This is because we can't ask for another stream.

}
;
webrtcCall.VideoConfig = function(isConference) {
  var that = this;
  that.profiles = globalVars.videoProfile

  var videoAspectRatio = {
    minAspectRatio: 1.777,
    maxAspectRatio: 1.778
  }
  var thumbnailAspectRatio = {
    minAspectRatio: 1.777,
    maxAspectRatio: 1.778,
    maxFrameRate: 8
  }

  var options = {}
  options[that.profiles.THUMBNAIL] = [
    {
      maxWidth: 160
    },
    {
      maxHeight: 90
    }
  ];
  options[that.profiles.SMALL] = [
    {
      maxWidth: 320
    },
    {
      maxHeight: 180
    }
  ];
  options[that.profiles.MEDIUM] = [
    {
      minWidth: 640
    },
    {
      minHeight: 360
    },
    {
      maxWidth: 640
    },
    {
      maxHeight: 360
    },
    {
      minFrameRate: 20
    }
  ];
  options[that.profiles.HIGH] = [
    {
      minWidth: 1280
    },
    {
      minHeight: 720
    }
  ];


  that.defaultVideoOptions = {
    mandatory: videoAspectRatio,
    optional: options[isConference ? that.profiles.MEDIUM : that.profiles.SMALL]
  }

  that.constraintsThumb = {
    audio: false,
    video: {
      mandatory: thumbnailAspectRatio,
      optional: options[that.profiles.THUMBNAIL]
    }
  }

  that.getConstraints = function(profile) {
    return {
      audio: false,
      video: {
        mandatory: videoAspectRatio,
        optional: options[profile]
      }
    }
  }


}
;
webrtcCall.VideoDirection = function(call, callEvents, connection, ui) {
  var that = this;
  var mediaVideo;
  var currentDirection;

  that.remoteWantToSendVideo = true;
  that.localWantToSendVideo = true;

  that.setMediaVideo = function(newMedia) {
    mediaVideo = newMedia;
    currentDirection = getMediaDirection(mediaVideo)
    that.remoteWantToSendVideo = isSendingVideo(currentDirection)
  }

  that.triggerEventsRemote = function() {
    //ui, to remove, should use the normal events
    if (that.remoteWantToSendVideo) {
      ui.enableRemoteVideo();
    } else {
      ui.disableRemoteVideo();
    }

    run_client_callback(weemo, 'onCallHandler', [call, {
      type: "video_remote",
      status: that.getVideoRemoteStatusText()
    }]);
    callEvents.trigger('video.remote.' + that.getVideoRemoteStatusText());
  }

  that.getVideoRemoteStatusText = function() {
    return that.remoteWantToSendVideo ? 'start' : 'stop';
  }
  that.getVideoLocalStatusText = function() {
    return that.localWantToSendVideo ? 'start' : 'stop';
  }


  function isSendingVideo(direction) {
    if (direction === "inactive" || direction === "recvonly")
      return false;
    else if (direction === "sendonly" || direction === "sendrecv")
      return true
    else
      throw new Error('Unknown video direction: ' + direction)
  }

  //default is start video
  function getMediaDirection(mediaVideo) {
    var direction = 'sendrecv';
    if (mediaVideo && mediaVideo[0] && mediaVideo[0].direction) {
      direction = mediaVideo[0].direction;
    }
    return direction
  }

  function updateRemoteStatus(remoteSendsVideo) {
    if (remoteSendsVideo) {
      that.remoteWantToSendVideo = true;
    } else {
      that.remoteWantToSendVideo = false;
    }
  }

  that.getDirection = function() {
    var newDirection = 'sendrecv'; // default
    if (that.localWantToSendVideo && !that.remoteWantToSendVideo)
      newDirection = 'sendonly'
    else if (!that.localWantToSendVideo && that.remoteWantToSendVideo)
      newDirection = 'recvonly'
    else if (!that.localWantToSendVideo && !that.remoteWantToSendVideo)
      newDirection = 'inactive'
    return newDirection
  }

  that.getMethodsToTest = function() {
    return {
      isSendingVideo: isSendingVideo,
      getMediaDirection: getMediaDirection,
      updateRemoteStatus: updateRemoteStatus
    }
  }

}


webrtcCall.VideoDirection.directions = {
  INACTIVE: 'inactive',
  RECVONLY: 'recvonly',
  SENDONLY: 'sendonly',
  SENDRECV: 'sendrecv'
}
;
webrtcCall.helper = {}

webrtcCall.helper.getSDPVideoMedia = function(sdpObject) {
  return arrayFilter(sdpObject.media, function(v) {
    return v.type === 'video'
  })
}


/*webrtcCall.helper.stopTracks = ...
webrtcCall.helper.findLineInRange = ...*/

webrtcCall.helper.sdpCleanup = function(sdp) {
  // Remove rtx related codec descriptions
  sdp = sdp.replace(/a=rtpmap:\d+ rtx\/90000\r\n/g, "");
  sdp = sdp.replace(/a=fmtp:\d+ apt=\d+\r\n/g, "");

  // Disable SSRC group
  var ssrc_group_line_position = sdp.search(/a=ssrc-group:FID \d+ \d+\r\n/);
  while (ssrc_group_line_position != -1) {
    var ssrc_tmp = sdp.slice(ssrc_group_line_position).split(" ")[2];
    var rtx_ssrc = ssrc_tmp.split("\r")[0];
    sdp = sdp.replace(/a=ssrc-group:FID \d+ \d+\r\n/, "");
    // Remove the second SSRC
    var ssrc_regex = new RegExp("a=ssrc:" + rtx_ssrc + " .+\r\n", 'g');
    sdp = sdp.replace(ssrc_regex, "");

    ssrc_group_line_position = sdp.search(/a=ssrc-group:FID \d+ \d+\r\n/);
  }
  return sdp;
}

webrtcCall.helper.log = function(m) {
  debug(m, {
    show_on_debug_level: 2
  })
}

webrtcCall.helper.defaultErrorHandling = debug
;
var pluginFacade = clone(driverFacade);

pluginFacade.msBetweenAccessAttemps = 500;
pluginFacade.requirePermissionFired = false;
pluginFacade.timeWaitedForAccess = 0;
pluginFacade.pluginInfo = {
  "name": "RTCCplugin",
  "activeXName": "Weemo.RTCCplugin"
};
;
pluginFacade.callback = function(type, args, callback) {

  if (globalVars.timeout.pluginConnect) {
    clearTimeout(globalVars.timeout.pluginConnect)
    globalVars.timeout.pluginConnect = false;
    debug('First message from the plugin', {
      show_on_debug_level: 2
    })
    debug('type: ' + type, {
      show_on_debug_level: 2
    })
    debug(args, {
      show_on_debug_level: 2
    })
  }

  switch (type) {
    case 'SendXml':
      weemo.responseManager.handle(args.xml);
      break
    case 'disconnect':
      triggerFacadeProxyClosed();
  }
};
;
/*
plugin connection steps :

call connect
if plugin is installed, load UI. If not, call connect until it is installed.
add plugin HTML to DOM
Loop until the plugin is loaded. if we wait too long, trigger the event plugin.requirepermission
trigger facade_proxy_opened

 */


pluginFacade.connect = function() {

  function isPluginInstalled() {
    if (global_config.forcePluginStatus !== undefined)
      return global_config.forcePluginStatus;
    if ('ActiveXObject' in window) {
      try {
        var plugin = new ActiveXObject(pluginFacade.pluginInfo.activeXName);
        return true;
      } catch (e) {
        debug(e);
        return false;
      }
    } else if (navigator.plugins) {
      navigator.plugins.refresh(false); //the browser refresh the plugins
      return navigator.plugins[pluginFacade.pluginInfo.name] !== undefined;
    }
  }

  function setPluginCallback() {
    if (globalVars.pluginObject.setCallback(pluginFacade.callback)) {
      debug("Plugin ready!");
      apiEvents.trigger('plugin.load')
      vent.trigger('facade_proxy_opened');
    } else {
      debug("Tried to set plugin callback");
      globalVars.timeout.pluginSetCallback = setTimeout(setPluginCallback, 500)
    }
  }

  function isPluginLoaded() {
    return weemoPluginLoaded === true;
  }

  function doWhenPluginLoaded(callback) {
    if (isPluginLoaded()) {
      pluginFacade.timeWaitedForAccess = 0;
      callback();
    } else {
      debug("Plugin not activated yet.", {
        show_on_debug_level: 1
      });
      triggerRequirePermission();
      globalVars.timeout.pluginDetection = setTimeout(doWhenPluginLoaded.bind(this, callback), pluginFacade.msBetweenAccessAttemps);
    }
  }

  function triggerRequirePermission() {
    pluginFacade.timeWaitedForAccess += pluginFacade.msBetweenAccessAttemps;
    if (!pluginFacade.requirePermissionFired && pluginFacade.timeWaitedForAccess > 5000) {
      apiEvents.trigger('plugin.requirepermission');
      pluginFacade.requirePermissionFired = true;
    }
  }


  if (isPluginInstalled()) {
    global_config.plugin = true;
    loadUi(function() {
      globalVars.pluginObject = globalVars.webRtcUi.getPlugin();
      doWhenPluginLoaded(setPluginCallback);
    })
  } else {
    triggerFacadeProxyClosed();
  }
};
;
pluginFacade.getConnectionMode = function() {
  return Rtcc.connectionModes.PLUGIN;
};
;
pluginFacade.open = function() {
  modeFacade = pluginFacade;
  setDriverRequests();
  setDriverConfig();

  clearTimeout(globalVars.timeout.pluginConnect); //stop the previous connect attempt, if any
  (function tryConnectPlugin() {
    globalVars.timeout.pluginConnect = setTimeout(tryConnectPlugin, global_config.timeBetweenConnectionAttempts)
    sendConnectDriver();
  })()
}
;
pluginFacade.removePlugin = function() {
  weemoPluginLoaded = false;
  globalVars.webRtcUi.destroy();
}
;
pluginFacade.send = function(message, debug_options) {
  message = message || "";
  debug_options = debug_options || {};

  debug_options.header = 'BROWSER >>>> SOCKET (PLUGIN)';
  debug(message, debug_options);
  globalVars.pluginObject.sendMessage('sendXml', {
    xml: message
  }, "");
  return;
};
;
/**
 * @class ClientCallRequest
 * @classdesc instanciated when a client has finishes the waiting in queue instanciated by Rtcc#onCallDistributorClientCallRequest callback
 *  @constructor
 * @param {String} uid - The uid of agent requestor

 **/
var ClientCallRequest = function(uid) {
  /**  uid of user **/
  this.uid = uid;
  /** The current state of the object can be "pending", "accepted", "denied" "canceled" */

  this.status = "pending"


  /**
   * accept client request
   **/
  this.accept = function() {
      this.status = 'accepted';
      weemo.requests.run('client_call_request', ['accept', this.uid]);

    }
    /**
     * decline client request
     **/

  this.decline = function() {
    this.status = 'declined';
    weemo.requests.run('client_call_request', ['decline', this.uid]);

  }


}
;
var downloadDriver = function() {
  run_client_callback(this, 'onRtccDriverNotStarted', [globalVars.downloadUrl]);
  apiEvents.trigger('driver.missing', globalVars.downloadUrl);
};

var downloadPlugin = function() {
  run_client_callback(this, 'onVideoPluginNotInstalled', [global_config.downloadUrl]);
  apiEvents.trigger('plugin.missing', globalVars.downloadUrl);
};
;
var get_global_config_defaults = function(mgmt_replacements) {
  return {
    debugLevel: 0,
    platform: navigator.platform,
    version: mgmt_replacements.version,
    max_skynet_request_size: 10,
    standAlone: false,
    force: false, //globalVars
    wsUri: "wss://localhost:34679",
    webpUri: 'ws://188.165.163.148:80',
    downloadUrl: mgmt_replacements.downloadUrl, //globalVars
    endpointUrl: mgmt_replacements.endpointUrl,
    forceNotWebRtcCompliant: false,
    forceWebRtcCompliant: false,
    forcePluginStatus: undefined, //undefined for no impact, used for testing
    hap_url: ['https://hap1.rtccloud.net/rtcc', 'https://hap2.rtccloud.net/rtcc'],
    current_hap: 0, //globalVars
    longpollUri: "https://localhost:34679", //34679
    callObjects: {}, //globalVars
    non_uid_ids_for_sending_messages: [], //globalVars
    hap: "prod/",
    protocol: 'weemodriver-protocol',
    meetingPointBeingCreated: false, // globalVars TODO find a better solution.
    connection_attempts_before_not_started_cb: 3,
    messageTimeout: 10000,
    bypassTurnProbeTest: false,
    probeProtocol: "wss",
    webpProtocol: "wss",
    force_chrome_allows_plugin: false,
    sixDigitNoCall: false,
    buttonDisabled: { //globalVars
      mute: false,
      video: false,
      share: false
    },
    iceConfig: ["turn:[turn_candidate]:3478?transport=udp", "turn:[turn_candidate]:3478?transport=tcp"],
    turn_probing_timeout: 3000,
    timeBetweenConnectionAttempts: 6000,
    pollingTimeout: 20000,
    interval_to_check_socket_closed: 1000,
    uiUrl: mgmt_replacements.uiBaseUrl + 'RtccUi.js',
    uiVersion: false,
    webp_timeout: 5000,
    webp_timebetweenpings: 10000,
    displayName: '',
    mode_parameter: mgmt_replacements.mode_parameter
  };
};
;
var globalVars = {
  state: Rtcc.STATES.NOT_CONNECTED_TO_FACADE,
  presence_state: Rtcc.PRESENCE_STATES.PRESNECE_NOK,
  token: null,
  call: false,
  sixDigitsCallMode: false,
  force_connect: false,
  downloadUrl: '@@DOWNLOAD_URL@@',
  timeout: {
    pluginConnect: false,
    pluginSetCallback: false,
    pluginDetection: false
  },
  videoProfile: {
    THUMBNAIL: 'ld',
    SMALL: 'sd',
    MEDIUM: 'md',
    HIGH: 'hd'
  },
  screenShareExtentionUrl: 'https://chrome.google.com/webstore/detail/screen-sharing/obcglfamidbohlfjlcfdajopagnhkgoo'
};
;
var weemo = this;


var joinRequestNotifications = {};
/**
 *
 * @class MeetingPointHost
 * @classdesc Meeting point actions as the conference host.
 *
 * <b> RTCCdriver and WebRTC</b>
 *
 * Returns a meeting point.
 * @constructor
 * @param {String} conftype - The type of conference you wish to create. can be  "permanent" |  "scheduled"| "adhoc"
 * @param {Object} options
 * @param {int} [options.startDate] - Unix timestamp of begining of conference
 * @param {int} [options.stopDate] - Unix Timestamp of end of conference
 * @param {String} [options.title] - Title of conference
 * @param {String} [options.location] - Location of conference
 **/

function MeetingPointHost(conftype, options) {
  options = options || {};

  if (conftype !== "permanent" && conftype !== "scheduled" && conftype !== "adhoc" && conftype !== "hostless") {
    throw "conftype " + conftype + "not allowed, allowed types are 'permanent', 'adhoc', 'scheduled', 'hostless'";
  }

  if (conftype === "scheduled" && (options.startDate === undefined || options.stopDate === undefined)) {
    throw "scheduled conftype require a startDate and an stopDate";
  }


  /** The current state of the object can be "created", "saved", "errorSaving", "errorModifing", "errorDeleting", "deleted", "started" */
  this.status = options.status || "created";

  /**
   * The conference type "permanent" | "scheduled" | "adhoc"
   */
  this.conftype = conftype;

  /**
   * <b> RtccDriver only </b>
   * Once hosted this variable will hold an element of {@link Rtcc.callType}
   */
  this.callType = undefined;

  /**
   * The host URL once it has been received from server
   * @private
   */
  this.hostUrl = options.hostUrl || false;


  /**
   *	The attendee URL once it has been received from server
   * @private
   */
  this.attendeeUrl = options.attendeeUrl || false;



  /** The meeting pointId once it has been received from server		*/
  this.id = options.id || false;


  /** The startDate of the meetingPoint	*/
  this.startDate = options.startDate || false;

  /**	The stopDate of the meeting point	*/
  this.stopDate = options.stopDate || false;


  /**	The attendees of the meeting point	*/
  this.attendees = {};

  /**	The location of the meetingPoint	*/
  this.location = options.location || '';


  /**	The title of the meeting point		 */
  this.title = options.title || '';

  /**	The mode of the meeting point		 */
  this.mode = options.mode || 'default';




  /**
   * <b> RTCCdriver and WebRTC</b><br />
   *
   * Function used to tell server to create meeting point.
   */
  this.create = function() {
    return weemo.requests.run("create_meeting_point", [this]);
  };

  /**
   *
   * <b> RTCCdriver </b>
   *
   * Flush all attendees from the Meeting Point
   * @private
   */

  this.flush = function() {
    this.attendees = {};
    weemo.requests.run("control_meeting_point", [this.id, "flush"]);
  };


  /**
   *
   * <b> RTCCdriver Only </b>
   *
   * List all attendees on the Meeting Point
   * @private
   */

  this.list = function() {
    weemo.requests.run("control_meeting_point", [this.id, "list"]);
  };



  /**
   * <b> RTCCdriver and WebRTC</b><br />

   * Modifies the meeting point
   * @param {object} options - Values to change
   * @param {int} [options.startDate] - Unix timestamp of begining of conference
   * @param {init} [options.stopDate] - Unix timestamp of end of conference
   * @param {String} [options.title] - Title of conference
   * @param {String} [options.location] - Location of the conference
   */
  this.modify = function(options) {
    options_to_be_applied = options;
    weemo.requests.run("modify_meeting_point", [this, options]);
  };
  var options_to_be_applied = false;

  this.modify_failure_callback = function() {
    options_to_be_applied = false;
  };
  this.modify_success_callback = function() {
    if (options_to_be_applied) {
      this.startDate = options_to_be_applied.startDate || this.startDate;
      this.stopDate = options_to_be_applied.stopDate || this.stopDate;
      this.title = (options_to_be_applied.title || this.title).decodeHTML();
      this.location = (options_to_be_applied.location || this.location).decodeHTML();
      options_to_be_applied = false;
    } else {
      debug("should only be called after a successfull modification");
    }
  };

  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Deletes this conf call
   **/
  this.remove = function() {
    return weemo.requests.run("delete_meeting_point", [this.id]);
  };
  var that = this;

  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Invites attendees to your meeting point
   * @param {String} uid - uid of attendee to invite
   */
  this.invite = function(uid) {
    // TODO include this method in the request lock system. //is this still valid ?
    weemo.requests.run("control_meeting_point", [this.id, "invite", uid]);

    this.attendees[uid] = new Attendee(this.id, uid);
  };

  /**
   *
   * <b> RTCCdriver and WebRTC</b>

   * Automatically denies all requests to join conference
   */

  this.lock_mode = function() {
    this.mode = "locked";
    weemo.requests.run("control_meeting_point", [this.id, this.mode]);
  };

  /**
   *
   * <b> RTCCdriver and WebRTC</b>

   * Toggles auto-accept or lock off.
   */
  this.default_mode = function() {
    this.mode = "default";
    weemo.requests.run("control_meeting_point", [this.id, this.mode]);
  };

  /**
   *
   * <b> RTCCdriver and WebRTC</b>

   * Auto-accepts all invites received
   */
  this.autoaccept_mode = function() {
    this.mode = 'auto-accept';
    weemo.requests.run("control_meeting_point", [this.id, this.mode]);
  };

  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   * Starts hosting the conference.
   * @param {String} callType (optional) an element of {@link Rtcc.callType} if not present defaults to Rtcc.callType.N_TO_N
   */

  this.host = function(callType) {
    weemo.requests.run("host_meeting_point", [this.id, callType]);
  };
}



/**
@class Attendee
@classdesc  This class represents an attendee on the host side, a meetingpoint instance can have many Attendee instances
@constructor
@param {String} uid - uid of attendee
@param {String} displayName - displayName of attendee
*/

var Attendee = function(meetingPointId, uid, displayName) {
  /** The id of the meeting point	 */
  this.id = meetingPointId;
  /**	* The uid of the attendee	 */
  this.uid = uid;
  /** * The displayName of the attendee	 */
  this.displayName = displayName;
  /**	* The status of attendee can be: "waitingForApproval", "ok", "nok"	*/
  this.status = "waitingForApproval";

  /**
   * Accepts attendee into conference
   */
  this.accept = function() {
    // TODO include in the lock request system. //is this still valid ?
    return weemo.requests.run("control_meeting_point", [this.id, "accept", this.uid]);
  };

  /** <b>Rtcc Driver only</b> <br/>The timestamp of the last modifications made to the attendee **/
  this.timestamp = undefined;


  /**
   * Does not allow requesting user to attend conference
   */
  this.deny = function() {
    return weemo.requests.run("control_meeting_point", [this.id, "deny", this.uid]);
  };
};

/**
 * @class MeetingPointAttendee
 * @classdesc Represents the attendee, on attendee side.
 *
 * <b> RTCCdriver and WebRTC</b>
 *
 * @constructor
 * @param {String} meetingPointId - the id of the meeting point
 **/
function MeetingPointAttendee(meetingPointId, hostDisplayName) {
  /**
   * The meeting point ID.
   */
  this.id = meetingPointId;

  /**
   * The display name of the host
   */
  this.hostDisplayName = hostDisplayName;

  /**
   * The current status of meetingpoint attendee can be "notJoined", "waitingForApproval", "attending", "denied"
   */
  this.status = "notJoined";

  /**
   * <b> RTCCdriver and WebRTC </b>
   *
   * Cancels a request to joing a conference.
   */
  this.cancel = function() {
    this.status = "cancel";
    weemo.requests.run("control_meeting_point", [this.id, this.status]);
  };


  /**
   *<b>Standalone mode only</b>
   * In standalone mode when an attendee gets an attendeeAccepted the confHash is passed so that the call can be made by the universal app.
   *
   **/
  this.confHash = false;

  /**
   * <b> RTCCdriver and WebRTC </b>
   *
   * Refuses a join invite
   **/
  this.deny = function() {
    this.status = "denied";
    weemo.requests.run("control_meeting_point", [this.id, "deny"]);

  };

  this.request = function() {
    this.status = "waitingForApproval";
    weemo.requests.run("attend_meeting_point", [this.id]);
  };

  /**
   * <b> WeemoDriver and WebRTC </b>
   *
   * Accepts a join invite
   */
  this.accept = function() {
    weemo.requests.run("control_meeting_point", [this.id, "accept"]);
    this.status = "ok";
    weemo.createCall(this.id, "attendee", 'conference');
  };
}


/**
 * @class JoinRequestNotification
 * @classdesc This is the object that is passed when a host hasn't yet hosted a conference, and an attendee enters
 * @constructor
 * @param {String} uid - uid of attendee
 * @param {String} displayName - displayName of attendee
 * @param {String} timestamp - timestamp of attendee
 * @param {String} mpi - meetingPointId
 **/
var JoinRequestNotification = function(params) {
  this.id = params.id;
  this.uid = params.uid;
  this.timestamp = params.timestamp;
  this.displayName = params.displayName;
  /**
   * <b> RTCCdriver and WebRTC </b>
   *
   * Deny an attendee
   **/
  this.deny = function() {
    weemo.requests.run("control_meeting_point", [this.id, "deny", this.uid]);
  };
};
;
  var DoInclude = {
    include: function(payload) {
      var merged_request;
      if (!payload["include"]) {
        return payload;
      }
      if (payload["include"] instanceof Array !== true) {
        payload["include"] = [payload["include"]];
      }
      var include_array = payload["include"].slice(0);
      delete payload["include"];
      while (include_array.length > 0) {
        var include_string = include_array.shift();
        if (!shared[include_string]) {
          throw new Error("object " + include_string + " does not exist");
        }
        payload = Rtcc.merge(shared[include_string], payload);
      }
      return this.include(payload);

    }
  };
;
var Request = function(command_delegates) {
  this.delegates = command_delegates || {};


};
Request.prototype.getDelegate = function(func_name, args) {
  if (typeof this.delegates[func_name] === "function") {
    return this.delegates[func_name];
  } else {
    return false;
  }
};
Request.prototype.notAllowed = function() {
  var delegate = this.getDelegate("notAllowed");
  if (delegate) {
    delegate.call(this.delegates);
  } else {
    debug("the command " + this.name + " is not allowed in this state");
  }
};

Request.prototype.allowed = function() {
  var delegate = this.getDelegate("allowed");
  if (delegate) {
    return delegate.call(this.delegates);
  } else {
    return true;
  }
};
Request.prototype.run = function() {
  if (this.allowed()) {
    if (typeof this.delegates.run !== "function") {
      debug("the command " + this.name + " is missing a run function");
      return false;
    }
    return this.delegates.run.apply(this.delegates, arguments) || true;
  } else {
    this.notAllowed();
    return false;
  }
};
;
var RequestManager = function(config) {
  var config = config || {};
  var requests = config.requests || {};

  this.getRequests = function() {
    return requests;
  };
  this.setRequests = function(new_requests) {
    var new_requests = clone(new_requests);
    requests = this.preProcessRequests(Object.keys(new_requests), new_requests);
    debug("requests for " + this.name + " have been successfully loaded");
  };

};
RequestManager.prototype = Rtcc.merge(RequestManager.prototype, DoInclude);

RequestManager.prototype.preProcessRequests = function(keys, requests) {
  return this.process(keys, requests, this.preProcessRequest);
};

RequestManager.prototype.preProcessRequest = function(key, request) {
  var merged_request = this.include(request);
  var request_instance = new Request(merged_request);
  request_instance.name = key;
  var post_request = {};
  post_request[key] = request_instance;
  return post_request;
};
RequestManager.prototype.process = function(keys, requests, callback) {
  if (keys.length === 0) {
    return {};
  }
  var key = keys.shift();
  var request = requests[key];

  return Rtcc.merge(callback.call(this, key, request), this.process(keys, requests, callback));
};

RequestManager.prototype.getRequest = function(name) {
  var requests = this.getRequests();
  var that = this;
  if (requests[name]) {
    return requests[name];
  } else {
    return {
      run: function() {
        debug("attempted to run request " + name + ", however this request does not exist for mode " + that.name);
      }
    };

  }
};

RequestManager.prototype.broadcast = function(function_name, args) {
  var that = this;
  var cb = function(key, request) {
    return request[function_name].apply(request, args);
  };
  this.process(Object.keys(this.getRequests()), this.getRequests(), cb);

};
RequestManager.prototype.runAll = function() {
  return this.broadcast("run", Array.prototype.slice.call(arguments, 0));
};
RequestManager.prototype.run = function(request_name, args) {
  if ((args instanceof Array) === false && args !== undefined) {
    throw new Error("Second parameter of run can only be undefined and an array");
  }
  var request = this.getRequest(request_name);
  if (args === undefined) {
    return request.run.apply(request);
  } else {
    return request.run.apply(request, args);
  }
};
;
var ResponseManager = function(parsers, handlers) {
  this.handlers = handlers;
  parsers = parsers || {};
  this.parsers = [];
  this.setParsers(parsers);
};

ResponseManager.prototype = Rtcc.merge(ResponseManager.prototype, DoInclude);



ResponseManager.prototype.setParsers = function(parsers) {
  this._setParsers(clone(parsers));

};

ResponseManager.prototype._setParsers = function(parsers) {
  this.parsers = [];
  if (parsers.preprocessor) {
    this.preprocessor = parsers.preprocessor.execute;
  }
  var keys = Object.keys(parsers);
  for (var i = 0; i < keys.length; i++) {
    if (keys[i] !== "preprocessor") {
      var parser = this.include(parsers[keys[i]]);
      var procesed_response = Rtcc.merge({
        name: keys[i]
      }, parser);
      this.parsers.push(procesed_response);
    }

  }

};
ResponseManager.prototype.parse = function(xml) {
  if (this.parsers.length === 0) {
    throw new Error("Parsers not set; use responseManager.setParsers");
  }
  var parsers = this.parsers.slice(0);
  var result;
  while (parsers.length > 0 && result === undefined) {
    var parser = parsers.shift();
    try {
      result = parser.parse(xml);
    } catch (error) {
      debug("parser " + parser.name + " produced an error when trying to parse the string:" + xml);
      debug(error.stack);
    }
  }
  if (result !== undefined) {
    result = [parser.name, result];
  }
  return result;
};

ResponseManager.prototype.doPreProcess = function(data) {
  if (typeof this.preprocessor === 'function') {
    try {
      return this.preprocessor(data);

    } catch (error) {
      debug("an error occured running the preprosesor function on " + data);
    }
  }
  return data;
};

ResponseManager.prototype.handle = function(data) {
  debug(data, {
    header: "SOCKET >>>> BROWSER"
  });
  var processed_data = this.doPreProcess(data);
  if (processed_data) {
    parsed_data = this.parse(processed_data);
    if (parsed_data !== undefined) {
      debug("message " + data + "parsed by parser " + parsed_data[0], {
        show_on_debug_level: 2
      });
      if (!this.handlers[parsed_data[0]]) {
        debug("no shared handler for " + parsed_data[0]);
        return true;
      }
      try {
        this.handlers[parsed_data[0]].handle.call(this.handlers[parsed_data[0]], parsed_data[1]);
        return true;
      } catch (error) {
        debug("the handler " + parsed_data[0] + " produced an error ");
        debug(error.stack);
      }
      return false;
    }
  }
};
;
var driver_requests = {
  attend_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id) {
    var xml_message = "<attendmeetingpoint><meetingpointid>" + id + "</meetingpointid></attendmeetingpoint>";
    modeFacade.send(xml_message);
  }
},
  broadcast_message:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uid, message) {
    debug("broadcast_message not yet supported in driver mode");
  }
},
  call_created:{
  run: function(params) {
    var callObjects = global_config.callObjects;
    var calledContact = global_config.calledContact;
    if (params.createdCallId !== "-1") {

      var call = new modeFacade.call(params.createdCallId, params.direction, params.displayNameToCall, global_config);
      globalVars.call = call;
      call.sipCallId = params.sipCallId;
      callObjects[params.createdCallId] = call;
      call.status.sound = "unmute";
      if (params.direction === "out") {
        if (calledContact === params.displayNameToCall) {
          call.status.call = "createdCall";
          run_client_callback(weemo, 'onCallHandler', [call, {
            type: "call",
            status: call.status.call
          }]);
          debug(call);
          if (start_in_audio_only) {
            start_in_audio_only = false;
            call.acceptNoVideo();
          } else {
            call.accept();
          }
        } else {
          debug("called contact does not match displayNameToCall");
        }
        global_config.calledContact = '';

        if (global_config.plugin) {
          globalVars.webRtcUi.ringing(call, true);
        }
      } else {
        call.status.call = "incoming";
        run_client_callback(weemo, 'onCallHandler', [call, {
          type: "call",
          status: "incoming"
        }]);

        if (global_config.plugin) {
          globalVars.webRtcUi.ringing(call, false);
        }
      }
      apiEvents.trigger('call.create', call)
    } else {
      debug("call has negative id");
    }
  }
},
  cancel_agent_request://driver
{
  include: ["allowed_after_presence_ok"],
  run: function() {
    modeFacade.send('<acdcancel></acdcancel>');
  }
},
  clear_toasts://driver
{
  run: function() {
    modeFacade.send('<cleartoasts></cleartoasts>');
  }
},
  client_call_request://driver
{
  include: ["allowed_after_presence_ok"],
  run: function(type, uid) {
    switch (type) {
      case "accept":
        modeFacade.send('<acdaccept>' + uid + '</acdaccept>')
        break;
      case "decline":
        modeFacade.send('<acddecline>' + uid + '</acddecline>')

        break;
    }
  }
},
  connect_to_cloud:{
  include: "allowed_after_connected",
  run: function(hap) {
    modeFacade.send("<connect hap='" + hap + "'></connect>");
  }
},
  control_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id, action, uid) {

    message = '<controlmeetingpoint><meetingpointid>' + id + '</meetingpointid><action>' + action + '</action>';
    if (uid) {
      message += '<uid>' + uid + '</uid>'
    }
    message += '</controlmeetingpoint>';

    modeFacade.send(message);

  }
},
  coredump:{
  run: function() {
    modeFacade.send('<coredump></coredump>');
  }
},
  create_call:{
  include: "allowed_after_sip_ok",
  run: function(params, is_audio_only) {
    var displayName = global_config.displayName;
    var hap = global_config.hap;
    start_in_audio_only = is_audio_only;
    if (displayName) {
      if (params.uidToCall && params.type && params.displayNameToCall) {
        global_config.calledContact = params.displayNameToCall;
        debug("Uid called : " + params.uidToCall);
        modeFacade.send("<createcall uid='" + params.uidToCall + "' displayname='" + params.displayNameToCall + "' type='" + params.type + "'></createcall>");
      } else {
        debug("uidToCall, type and displayNameToCall must be set");
      }
    } else {
      debug("caller displayName must be set");
      run_client_callback(weemo, 'onConnectionHandler', ['error', 16]);
      apiEvents.trigger('error', 16)
    }
  }
},
  create_meeting_point:{
  include: ["allowed_after_verified_user_ok", "xml_utils"],
  run: function(obj) {
    var xml_message = "<createmeetingpoint><type>" + obj.conftype + "</type>";
    xml_message += this.buildXmlArgs.call(obj);
    xml_message += "</createmeetingpoint>";
    modeFacade.send(xml_message);
  }
},
  create_six_digits:{
  include: "allowed_after_sip_ok",
  run: function(mode_parameter, displayName, mpi) {
    var mpi_str = '';
    if (mpi) {
      mpi_str = ' mpi="' + mpi + '"'
    }
    modeFacade.send('<createsixdigits mode="' + mode_parameter + '"' + mpi_str + '>' + displayName + '</createsixdigits>');
  }
},
  delete_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id) {
    var xml_message = "<deletemeetingpoint><meetingpointid>" + id + "</meetingpointid></deletemeetingpoint>";
    modeFacade.send(xml_message);
  }
},
  delete_six_digits://driver
{
  include: "allowed_after_sip_ok",
  run: function() {
    modeFacade.send('<deletesixdigits></deletesixdigits>');
  }
},
  drop_all_attendees:{
  include: "allowed_after_verified_user_ok",
  run: function(obj) {
    modeFacade.send('<controlcall id="' + obj.callId + '"><conference>dropallattendees</conference></controlcall>');
  }
},
  get_call_window_default_position:{
  run: function() {
    modeFacade.send('<get type="callwindowdefaultposition" />');
  }
},
  get_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(meetingPointId) {
    var message = "<getmeetingpoint><meetingpointid>" + meetingPointId + "</meetingpointid></getmeetingpoint>";
    modeFacade.send(message);
  }
},
  get_permanent_meeting_point_by_uid:{
  include: "allowed_after_verified_user_ok",
  run: function(uid) {
    modeFacade.send('<getpermanentmeetingpoint><uid>' + uid + '</uid></getpermanentmeetingpoint>');
  }
},
  get_presence:{
  include: ["chunckable", "allowed_after_presence_ok", "roster_xml_builder"],
  run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send(this.toXml("presenceget", chunks.next));
    }
    if (chunks.remainder) {
      this.run(chunks.remainder);
    }
  }
},
  get_roster:{
  include: "allowed_after_presence_ok",
  run: function() {
    modeFacade.send("<rosterget></rosterget>");
  }
},
  get_status:{
  include: "allowed_after_sip_ok",
  run: function(uidStatus) {
    modeFacade.send("<get type='status' uid='" + uidStatus + "' />");
  }
},
  get_version:{
  run: function() {
    modeFacade.send("<get type='version'></get>");
  }
},
  get_wait_list://driver
{
  include: ["allowed_after_presence_ok"],
  run: function() {
    modeFacade.send('<acdgetwaitinglist></acdgetwaitinglist>');
  }
},
  get_wall_settings:{
  include: "allowed_after_verified_user_ok",
  run: function() {
    modeFacade.send('<getwall/>');
  }
},
  host_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id, mode) {
    var mode_str = '';
    if (mode !== undefined) {
      mode_str = ' mode="' + mode + '"';
    }
    var xml_message = '<hostmeetingpoint' + mode_str + '><meetingpointid>' + id + '</meetingpointid></hostmeetingpoint>';
    modeFacade.send(xml_message);
  }
},
  modify_meeting_point:{
  include: ["allowed_after_verified_user_ok", "xml_utils"],
  run: function(obj, options) {
    var xml_message = "<modifymeetingpoint><meetingpointid>" + obj.id + "</meetingpointid><type>" + obj.conftype + "</type>";
    xml_message += this.buildXmlArgs.call(obj, options);
    xml_message += "</modifymeetingpoint>";
    modeFacade.send(xml_message);
  }
},
  request_agent://driver
{
  include: ["allowed_after_presence_ok"],
  run: function(data) {
    modeFacade.send('<acdgetsingleuser><mask>' + data.mask + '</mask><value>' + data.value + '</value></acdgetsingleuser>');
  }
},
  request_agent_list://driver
{
  include: ["allowed_after_presence_ok"],
  run: function(data) {
    modeFacade.send('<acdgetuserlist><mask>' + data.mask + '</mask><value>' + data.value + '</value></acdgetuserlist>');
  }
},
  reset:{
  run: function() {
    modeFacade.send('<reset></reset>');
  }
},
  roster_add:{
  include: ["chunckable", "allowed_after_presence_ok", "roster_xml_builder"],
  run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send(this.toXml("rosteradd", chunks.next));
    }
    if (chunks.remainder) {
      this.run(chunks.remainder);
    }
  }
},
  roster_clear:{
  include: "allowed_after_presence_ok",
  run: function() {
    modeFacade.send('<rosterclear></rosterclear>');
  }
},
  roster_remove:{
  include: ["chunckable", "allowed_after_presence_ok", "roster_xml_builder"],
  run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send(this.toXml("rosterremove", chunks.next));
    }
    if (chunks.remainder) {
      this.run(chunks.remainder);
    }
  }
},
  send_acknowledge:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uid, status) {
    var xml_message = '<messageack to="' + uid + '" id="' + message_id + '">' + status + '</messageack>'
    modeFacade.send(xml_message);
  }

},
  send_data_channel_message:{
  include: "allowed_after_sip_ok",
  run: function(id, message) {
    var aMyUTF8Input = strToUTF8Arr(message);
    var base64 = "a" + base64EncArr(aMyUTF8Input);
    if (arrayContains(global_config.non_uid_ids_for_sending_messages, Number(id))) {
      modeFacade.send("<reply to='" + id + "'>" + base64 + "</reply>");
    } else {
      modeFacade.send("<message to='" + id + "'>" + base64 + "</message>");
    }
  }
},
  send_display_name:{
  include: "allowed_after_verified_user_ok",
  run: function(name) {
    modeFacade.send("<set displayname='" + name.encodeHTML() + "'></set>");
  }
},
  send_inband_message:{
  include: "allowed_after_sip_ok",
  run: function(message) {
    modeFacade.send('<sendinband>' + message.encodeHTML() + '</sendinband>');
  }
},
  send_message:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uid, message) {
    var xml_message = '<presencemessage to="' + uid + '" id="' + message_id + '">' + message.encodeHTML() + '</presencemessage>'
    modeFacade.send(xml_message);
  }

},
  set_auto_erase_threshold://driver
{
  include: "allowed_after_sip_ok",
  run: function(data) {
    var dataValue;
    dataValue = Number(data);
    if (isNaN(dataValue) || dataValue < 0 || dataValue > 1000) {
      throw new Error('auto_erase_threshold expects values between 0 and 10000');
    }
    modeFacade.send('<set autoerasethr="' + dataValue + '"/>');
  }
},
  set_call_window_default_position:{
  run: function(val) {
    modeFacade.send('<set callwindowdefaultposition="' + val + '"></set>');
  }
},
  set_disabled_buttons:{
  castOption: function(value) {
    if (value === true) {
      return "1";
    } else {
      return "0";
    }
  },
  makeBinaryRepresentation: function(options) {
    var string = "";
    string += this.castOption(options.mute);
    string += this.castOption(options.video);
    string += this.castOption(options.share);
    return string;

  },
  run: function(options) {
    global_config.buttonDisabled = Rtcc.merge(global_config.buttonDisabled, options);
    var binaryString = this.makeBinaryRepresentation(global_config.buttonDisabled);
    var translatedForDriver = parseInt(binaryString.split('').reverse().join(''), 2);
    modeFacade.send('<set disabledbuttons="' + translatedForDriver + '"/>');
  }
},
  set_ice_mode:{
  include: "allowed_after_sip_ok",
  run: function(mode_parameter) {
    modeFacade.send("<set icemode='" + mode_parameter + "'></set>");
  }
},
  set_js_api_version_to_driver://driver
{
  run: function(version) {
    modeFacade.send('<set version="' + version + '" />')
  }
},
  set_my_acd_presence://driver
{
  include: "allowed_after_presence_ok",
  run: function(value) {
    modeFacade.send('<acdpresenceset>' + value + '</acdpresenceset>');
  }
},
  set_my_presence:{
  include: ["allowed_after_presence_ok", "my_presence_validate_input"],
  run: function(presence_id) {
    this.validateInput(presence_id);
    modeFacade.send("<presenceset>" + presence_id + "</presenceset>");
  }
},
  set_overlay://driver
{
  run: function(mode) {
    modeFacade.send('<set overlay="' + mode + '"/>');
  }
},
  set_pickup_mode:{
  include: "allowed_after_sip_ok",
  run: function(pickup_mode) {
    modeFacade.send('<set pickupmode="' + pickup_mode + '"/>');
  }
},
  set_plugin_mode://driver
{
  run: function(mode) {
    modeFacade.send('<set pluginmode="' + mode + '"/>');
  }
},
  set_startup_profile:{
  include: "allowed_after_sip_ok",
  run: function(startup_profile) {
    modeFacade.send('<set startupprofile="' + startup_profile + '"/>');
  }
},
  set_startup_size:{
  include: "allowed_after_sip_ok",
  run: function(starup_size) {
    modeFacade.send('<set startupsize="' + starup_size + '"/>');
  }
},
  set_test_mode://driver
{
  run: function(mode) {
    modeFacade.send('<set testmode="' + (+mode) + '"/>')
  }
},
  set_url_referer://driver
{
  run: function(url) {
    modeFacade.send('<set urlreferer="' + url + '" />');
  }
},
  set_user_agent://driver
{
  run: function() {
    modeFacade.send('<set ua="' + global_config.browser + ' ' + global_config.browserVersion + '"/>');
  }
},
  sip_register://driver
{
  run: function() {
    debug("request not implemented in mode driver");
  }
},
  toast://driver
{
  run: function(options) {
    if (options.type === undefined) {
      throw new Error("param `type` is required");
    } else if (options.type !== "message" && options.type !== "info") {
      throw new Error("type `" + options.type + "` does not exist, allowed types are `info` and `message`");
    }
    if (options.message === undefined) {
      throw new Error("param `message` is required");
    }
    if (options.type === "message" && options.from === undefined) {
      throw new Error("param `from` is required for toast of type `message`");
    }
    if (options.timeout === undefined) {
      options.timeout = 5;
    }
    var fromStr = " ";
    if (options.type === "message") {
      fromStr = ' from="' + options.from + '" ';
    }
    modeFacade.send('<toast type="' + options.type + '"' + fromStr + 'timeout="' + options.timeout + '">' + options.message + '</toast>');
  }
},
  update_wall_settings:{
  include: "allowed_after_verified_user_ok",
  run: function(options) {
    var str = ""
    objectForEach(options, function(k, v) {
      if (v !== undefined)
        str += "<" + k + ">" + v.encodeHTML() + "</" + k + ">"
    })
    modeFacade.send("<updatewall>" + str + "</updatewall>");
  }
},
  verify_user:{
  run: function(type) {
    run_client_callback(weemo, 'onConnectionHandler', ["connectedRtccDriver", 0]);
    apiEvents.trigger('client.connect', weemo.getConnectionMode());
    var token = globalVars.token;
    var force = globalVars.force_connect;
    var appId = global_config.appId;
    var rtccUserType = global_config.rtccUserType;
    var appendToCommand = '';
    if (force === true) {
      appendToCommand = " force='1'";
    } else if (type === "bypass") {
      appendToCommand = " bypass='1'";
    } else if (rtccUserType === "external") {
      rtccUserType = 'ls_external';
      appendToCommand = " suffix='" + generateSuffix() + "'";
    }
    modeFacade.send("<verifyuser token='" + token + "' urlreferer='" + appId + "' type='" + rtccUserType + "'" + appendToCommand + "></verifyuser>");
    globalVars.force_connect = false;
  }
}};;
var webrtc_requests = {
  attend_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id) {
    var message = {
      cmd: "attendmeetingpoint",
      args: [id]
    }
    modeFacade.send(message);
  }
},
  broadcast_message:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uids, message) {
    modeFacade.send({
      cmd: "dc_multiple_send",
      args: [message_id, uids, message]
    })
  }

},
  call_created:{
  run: function(params) {
    var direction = params[0];
    var callId = Number(params[1]);
    var displayName = params[2];
    var call = new modeFacade.call(callId, params, displayName, global_config);
    globalVars.call = call;
    var connection = call.getConnection();
    connection.status.sound = "unmute";
    if (direction === "out") {
      debug(call);
      if (start_in_audio_only) {
        start_in_audio_only = false;
        call.acceptNoVideo();
      } else {
        call.accept();
      }
    }
    global_config.callObjects[callId] = call;
    apiEvents.trigger('call.create', call)
  }
},
  cancel_agent_request://webrtc
{
  include: ["allowed_after_presence_ok"],
  run: function() {
    modeFacade.send({
      "cmd": "acd_cancelwait",
      "args": []
    });
  }
},
  client_call_request://webrtc
{
  include: ["allowed_after_presence_ok"],
  run: function(type, uid) {
    modeFacade.send({
      "cmd": "acd_request",
      "args": [type, uid]
    })
  }
},
  control_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id, action, uid) {

    var message = {
      cmd: "controlmeetingpoint",
      args: [id, action]
    }
    if (uid) {
      message.args.push(uid);
    }
    modeFacade.send(message);

    return message;
  }
},
  coredump:{
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  create_call:{
  include: "allowed_after_sip_ok",
  run: function(params, is_audio_only) {
    start_in_audio_only = is_audio_only;
    var msg = {
      cmd: "createcall",
      args: [params.uidToCall, params.displayNameToCall, params.type]
    };
    modeFacade.send(msg);
  }
},
  create_meeting_point:{
  include: ["allowed_after_verified_user_ok", "json_utils"],
  run: function(obj) {
    var message = {
      cmd: "createmeetingpoint",
      args: this.buildJsonArgs.call(obj, [obj.conftype])
    }
    modeFacade.send(message);

    return message;
  }
},
  create_six_digits:{
  include: "allowed_after_sip_ok",
  run: function(mode, displayName, mpi) {
    var data = {
      mode: mode,
      display_name: displayName
    }
    if (mpi) data.mpi = mpi;

    modeFacade.send({
      "cmd": "createsixdigits",
      "args": data
    });
  }
},
  delete_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id) {
    var message = {
      cmd: "deletemeetingpoint",
      args: [id]
    }
    modeFacade.send(message);
  }
},
  delete_six_digits://webrtc
{
  include: "allowed_after_sip_ok",
  run: function() {
    modeFacade.send({
      cmd: "deletesixdigits",
      args: {}
    });
  }
},
  drop_all_attendees:{
  include: "allowed_after_verified_user_ok",
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  get_call_window_default_position:{
  run: function() {
    debug("request not implemented in mode webrtc");
    run_client_callback(weemo, 'onConnectionHandler', ['notUseInThisMode', 0]);
    apiEvents.trigger('error.unavailable')
  }
},
  get_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(meetingPointId) {
    message = {
      "cmd": "getmeetingpoint",
      "args": [
        meetingPointId
      ]
    }
    modeFacade.send(message);
  }
},
  get_permanent_meeting_point_by_uid:{
  include: "allowed_after_verified_user_ok",
  run: function(uid) {
    modeFacade.send({
      "cmd": "getpermanentmeetingpoint",
      "args": [uid]
    });
  }
},
  get_presence:{
  include: ["chunckable", "allowed_after_presence_ok"],
  run: function(uid_array) {
    this._run(uid_array.slice(0));
  },
  _run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send({
        "cmd": "presence_get",
        "args": chunks.next
      });
    }
    if (chunks.remainder) {
      this._run(chunks.remainder);
    }
  }
},
  get_roster:{
  include: "allowed_after_presence_ok",
  run: function() {
    modeFacade.send({
      cmd: "presence_getwholeroster",
      args: []
    });
  }
},
  get_status:{
  include: "allowed_after_sip_ok",
  run: function(uidStatus) {
    var msg = {
      cmd: "get",
      args: ['status', uidStatus]
    };
    modeFacade.send(msg);
  }
},
  get_version:{
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  get_wait_list://webrtc
{
  include: ["allowed_after_presence_ok"],
  run: function() {
    modeFacade.send({
      "cmd": "acd_getwaitingqueue",
      "args": []
    })
  }
},
  get_wall_settings:{
  include: "allowed_after_verified_user_ok",
  run: function() {
    modeFacade.send({
      cmd: "getwall",
      args: []
    });
  }
},
  host_meeting_point:{
  include: "allowed_after_verified_user_ok",
  run: function(id, mode) {
    mode = mode || Rtcc.callType.N_TO_N;
    var message = {
      cmd: "hostmeetingpoint",
      args: [id, mode]
    }

    modeFacade.send(message);
  }
},
  modify_meeting_point:{
  include: ["allowed_after_verified_user_ok", "json_utils"],
  run: function(obj, options) {
    var message = {
      cmd: "modifymeetingpoint",
      args: this.buildJsonArgs.call(obj, [obj.id], options)
    }
    modeFacade.send(message);
  }
},
  request_agent://webrtc
{
  include: 'allowed_after_presence_ok',
  run: function(data) {
    modeFacade.send({
      "cmd": "acd_getsingleuser",
      "args": [data.mask, data.value]
    });
  }
},
  request_agent_list://webrtc
{
  include: 'allowed_after_presence_ok',
  run: function(data) {
    modeFacade.send({
      "cmd": "acd_getuserlist",
      "args": [data.mask, data.value]
    });
  }
},
  reset:{
  run: function() {
    weemo.disconnect();
  }
},
  roster_add:{
  include: ["chunckable", "allowed_after_presence_ok"],
  run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send({
        "cmd": "roster_add",
        "args": chunks.next
      });
    }
    if (chunks.remainder) {
      this.run(chunks.remainder);
    }
  }
},
  roster_clear:{
  include: "allowed_after_presence_ok",
  run: function() {
    modeFacade.send({
      "cmd": "roster_clear",
      "args": []
    });
  }
},
  roster_remove:{
  include: ["chunckable", "allowed_after_presence_ok"],
  run: function(uid_array) {
    if (!uid_array instanceof Array) {
      throw "expects an array"
    }
    var chunks = this.getNextChunk(uid_array, global_config.max_skynet_request_size);
    if (chunks.next) {
      modeFacade.send({
        "cmd": "roster_remove",
        "args": chunks.next
      });
    }
    if (chunks.remainder) {
      this.run(chunks.remainder);
    }
  }
},
  send_acknowledge:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uid, status) {
    modeFacade.send({
      cmd: "dc_acksend",
      args: [message_id, uid, status]
    })
  }

},
  send_data_channel_message:{
  include: "allowed_after_sip_ok",
  run: function(id, message) {
    var aMyUTF8Input = strToUTF8Arr(message);
    var base64 = "a" + base64EncArr(aMyUTF8Input);
    if (arrayContains(global_config.non_uid_ids_for_sending_messages, Number(id))) {
      modeFacade.send({
        cmd: "message_reply",
        args: [id, base64]
      });
    } else {
      modeFacade.send({
        cmd: "message",
        args: [id, base64]
      });
    }
  }
},
  send_display_name:{
  include: "allowed_after_verified_user_ok",
  run: function(name) {
    var msg = {
      "cmd": "set",
      "args": [
        "displayname",
        name
      ]
    };
    modeFacade.send(msg);
  }
},
  send_inband_message:{
  run: function(message) {
    webRtcChannelWrapper.send(message);
  }
},
  send_message:{
  include: ["allowed_after_presence_ok"],
  run: function(message_id, uid, message) {
    modeFacade.send({
      cmd: "dc_send",
      args: [message_id, uid, message]
    })
  }

},
  set_call_window_default_position:{
  run: function() {
    debug("request not implemented in mode webrtc")
    run_client_callback(weemo, 'onConnectionHandler', ['notUseInThisMode', 0]);
    apiEvents.trigger('error.unavailable', 'setCallWindowDefaultPosition')
  }
},
  set_disabled_buttons:{
  include: "allowed_after_sip_ok",
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  set_ice_mode:{
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  set_my_acd_presence://webrtc
{
  include: "allowed_after_presence_ok",
  run: function(value) {
    modeFacade.send({
      cmd: "acd_presence_set",
      "args": [value]
    });
  }
},
  set_my_presence:{
  include: ["allowed_after_presence_ok", "my_presence_validate_input"],
  run: function(presence_id) {
    this.validateInput(presence_id);
    modeFacade.send({
      cmd: "presence_set",
      args: [presence_id]
    });
  }
},
  set_pickup_mode:{
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  set_startup_profile:{
  include: "allowed_after_sip_ok",
  run: function(startup_size) {
    global_config.webRtcUi.setStartupSize(startup_size);
  }
},
  set_startup_size:{
  run: function() {
    debug("request not implemented in mode webrtc")
  }
},
  set_test_mode://webrtc
{
  run: function() {
    debug("request not implemented in mode webrtc");
  }
},
  set_url_referer://webrtc
{
  run: function() {
    debug("request not implemented in mode webrtc");
  }
},
  sip_register://webrtc
{
  run: function() {
    modeFacade.send({
      "cmd": "sip_register",
      "args": []
    });
  }
},
  update_wall_settings:{
  include: "allowed_after_verified_user_ok",
  run: function(options) {
    modeFacade.send({
      cmd: "updatewall",
      args: [options]
    });
  }
},
  verify_user:{
  run: function(type) {
    if (type === 'bypass') {
      debug("bypass not implemented in mode webrtc")
      return;
    }
    if (global_config.standAlone) {
      run_client_callback(weemo, 'onConnectionHandler', ["connectedNoSip", 0]);
      apiEvents.trigger('cloud.nosip.connect')
    } else {
      run_client_callback(weemo, 'onConnectionHandler', ["connectedWebRTC", 0]);
      apiEvents.trigger('client.connect', Rtcc.connectionModes.WEBRTC);
    }
    var token = globalVars.token;
    var appId = global_config.appId;
    var rtccUserType = global_config.rtccUserType;

    var platform = global_config.platform;
    var platformToMgmt = "";
    if (platform.match(/mac/i) !== null) {
      platformToMgmt = "mac";
    } else if (platform.match(/win/i) !== null) {
      platformToMgmt = "pc";
    } else if (platform.match(/linux/i) !== null) {
      platformToMgmt = "linux";
    } else {
      platformToMgmt = platform;
    }
    var sip_mode;
    if (global_config.standAlone) {
      sip_mode = "standalone";
    } else {
      sip_mode = "not_standalone";
    }
    var args;
    if (rtccUserType === "external") {
      args = [appId, token, "ls_external", platformToMgmt, sip_mode, generateSuffix()]

    } else {
      args = [appId, token, rtccUserType, platformToMgmt, sip_mode]
    }


    var msg = {
      cmd: "verifyuser",
      args: args
    };
    modeFacade.send(msg);
  }
}};;
var driver_parsers = {
  acknowledge_received:{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("messageack")[0];
    if (message) {
      var options = {};

      options.uid = message.getAttribute("from");
      options.message_id = message.getAttribute("id");
      options.status = message.childNodes[0].nodeValue;
      return options;
    }
  }
},
  agent_or_queue_received://driver
{
  convertPresencePayload: function(roster) {
    if (roster.childNodes.length === 0) {
      return [];
    } else {
      var child = roster.childNodes[0];
      roster.removeChild(child);
      return [{
        uid: child.childNodes[0].nodeValue,
        presence: child.getAttribute("presence")
      }].concat(this.convertPresencePayload(roster))
    }
  },
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("acduserlist")[0];
    if (message) {
      var options = {}
      var queue = message.getElementsByTagName('queue')[0]
      if (queue) {
        options.queue = {
          position: Number(queue.childNodes[0].nodeValue),
          length: Number(queue.getAttribute("len"))
        }
      } else {
        options = {
          queue: {
            position: 0,
            length: 0
          },
          agents: {
            length: Number(message.getAttribute("len")),
            uid_array: this.convertPresencePayload(message)
          }
        }
      }
      return options;
    }
  }
},
  audio_receieved://driver
{
  parse: function(xmlDoc) {
    var status = xmlDoc.getElementsByTagName("status")[0];
    if (status) {
      var audio = status.getElementsByTagName("audio")[0];
      if (audio) {
        if (audio.childNodes[0].nodeValue === "ok") {
          return "ok";
        } else {
          return "nok";
        }
      }
    }
  }
},
  call_audio_received://driver
{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("audioreceived")[0];
    if (message) {
      return true;
    }
  }
},
  call_created://driver
{
  parse: function(xmlDoc) {
    createdcall = xmlDoc.getElementsByTagName("createdcall")[0];
    if (createdcall) {
      var params = {}

      var sipCallId = createdcall.getElementsByTagName('sipcallid')[0];
      if (sipCallId) {
        params.sipCallId = sipCallId.childNodes[0].nodeValue;
      }
      params.createdCallId = createdcall.getAttribute("id");
      params.direction = createdcall.getAttribute("direction");
      params.displayNameToCall = createdcall.getAttribute("displayname");
      return params;
    }
  }
},
  call_status_received://driver
{
  current_share_list: [],
  parse: function(xmlDoc) {
    statuscall = xmlDoc.getElementsByTagName("statuscall")[0];

    if (statuscall) {
      var params = {};
      params.id = statuscall.getAttribute('id');
      var sipidTag = statuscall.getElementsByTagName("sipcallid")[0];
      if (sipidTag) {
        params.sipCallId = sipidTag.childNodes[0].nodeValue;
      }
      var call = statuscall.getElementsByTagName("call")[0];
      if (call) {
        params.type = "call";
        params.status = call.childNodes[0].nodeValue;
        if (params.status == "terminated") {
          var reason = statuscall.getElementsByTagName("reason")[0];
          params.reason = reason.childNodes[0].nodeValue;
        }
        return params;
      }
      var video_local = statuscall.getElementsByTagName("video_local")[0];
      if (video_local) {
        params.type = "video_local";
        params.status = video_local.childNodes[0].nodeValue;
        return params;
      }

      var video_remote = statuscall.getElementsByTagName("video_remote")[0];
      if (video_remote !== undefined && video_remote !== null) {
        params.type = "video_remote";
        params.status = video_remote.childNodes[0].nodeValue;
        return params;
      }
      var share_local = statuscall.getElementsByTagName("share_local")[0];
      if (share_local) {
        params.type = "share_local";
        params.status = share_local.childNodes[0].nodeValue;
        return params;
      }
      var share_remote = statuscall.getElementsByTagName("share_remote")[0];
      if (share_remote) {
        params.type = "share_remote";
        params.status = share_remote.childNodes[0].nodeValue;
        return params;
      }
      var sound = statuscall.getElementsByTagName("sound")[0];
      if (sound) {
        params.type = "sound";
        params.status = sound.childNodes[0].nodeValue;
        return params;
      }
      var record = statuscall.getElementsByTagName("record")[0];
      if (record) {
        params.type = "record";
        params.status = record.childNodes[0].nodeValue;
        var filename = statuscall.getElementsByTagName("filename")[0];
        if (filename) {
          params.filename = filename.childNodes[0].nodeValue;
        }
        return params
      }
      var share_list = statuscall.getElementsByTagName("share_list")[0];
      if (share_list) {
        params.type = "share_local_list";
        params.item_number = parseInt(share_list.getAttribute('nitems'), 10);
        var app = statuscall.getElementsByTagName('app')[0];
        params.item_id = app.getAttribute('id');
        params.item_name = app.childNodes[0].nodeValue;
        return params;
      }

      var frame_width = statuscall.getElementsByTagName("remvidwidth")[0];
      var frame_height = statuscall.getElementsByTagName("remvidheight")[0];
      if (frame_height && frame_width) {
        params.type = 'frame_size';
        params.height = Number(frame_height.childNodes[0].nodeValue);
        params.width = Number(frame_width.childNodes[0].nodeValue);
        return params;
      }

      var datachannel = statuscall.getElementsByTagName("datachannel")[0];
      if (datachannel) {
        params.type = 'datachannel';
        params.status = datachannel.getAttribute('status');
        return params;
      }

      var json = JXON.xmlDoc2jsonObject(xmlDoc).statuscall;
      var i;

      if (json.conference) {
        var conference = {};

        var pList = {};
        json.id = json['@id'];
        delete json['@id'];
        if (json.conference.status) {
          var participantsStatus = [];
          if (!isArray(json.conference.status.p)) {
            json.conference.status.p = [json.conference.status.p]
          }
          for (i = 0; i < json.conference.status.p.length; i++) {
            var participant = json.conference.status.p[i];
            participantsStatus.push({
              id: participant.id,
              mute: (participant.mute === "true"),
              deaf: (participant.deaf === "true"),
              video: (participant.video === "true")
            })
          }
          conference.participantsStatus = participantsStatus;
        }
        if (json.conference.floor) {
          conference.floor = json.conference.floor.p;
          if (!isArray(conference.floor)) {
            conference.floor = [conference.floor]
          }
        } else if (json.conference.list) {
          if (!isArray(json.conference.list.p)) {
            json.conference.list.p = [json.conference.list.p]
          }

          var participants = [];
          for (i = 0; i < json.conference.list.p.length; i++) {
            participants.push({
              id: json.conference.list.p[i].id,
              displayName: json.conference.list.p[i].n
            })
          }
          pList.hostId = json.conference.host;
          pList.myId = json.conference.mypid;
          pList.participants = participants;
          conference.participantList = pList
        }
        json.conference = conference

      }
      return json;
    }
  }
},
  call_video_received://driver
{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("videoreceived")[0];
    if (message) {
      var options = {};
      return true;
    }
  }
},
  client_call_requested://driver
{
  parse: function(xmlDoc) {
    var message, options;
    message = xmlDoc.getElementsByTagName("acdrequested")[0];
    if (message) {
      options = {
        type: 'requested',
        uid: message.childNodes[0].nodeValue
      };
      return options;
    }

    message = xmlDoc.getElementsByTagName("acdcanceled")[0];
    if (message) {
      options = {
        type: 'canceled',
        uid: message.childNodes[0].nodeValue
      };
      return options;
    }
  }
},
  conference_status://driver
{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("conference_status")[0];
    if (message) {
      var options = {};
      //return options;
    }
  }
},
  dropped_received://driver
{
  parse: function(xmlDoc) {
    var dropped = xmlDoc.getElementsByTagName("dropped")[0];
    if (dropped) {
      return true;
    }
  }
},
  error_received://driver
{
  include: 'xml_utils',
  parse: function(xmlDoc) {
    if (xmlDoc.firstChild && xmlDoc.firstChild.nodeName === "error") {
      var error = xmlDoc.firstChild;
      var params = {};
      if (error.childNodes[0]) {
        params.message = error.childNodes[0].nodeValue;
      }

      switch (params.message) {
        case "1":
          globalVars.state = Rtcc.STATES.CONNECTED_TO_FACADE;
          debug("Should Not Be used (err " + params.error + ")");
          break;

        case "2":
          debug("Long poll: Wrong WebService init session (err " + params.error + ")");
          break;

        case "3":
          debug("Should Not Be used (err " + params.error + ")");
          break;

        case "4":
          debug("only connect, and coredump are allowed right after connection (err " + params.error + ")");
          break;

        case "5":
          debug("XML command parsing error, or <connect> received with a different HAP setting, or unrecognized command in current WD state (err " + params.error + ")");
          break;

        case "6":
          debug("Received command rejected, as the user is not yet authenticated in MAPI." + params.error + ")");
          break;

        case "7":
          run_client_callback(weemo, 'onConnectionHandler', ["error", params.message]);
          apiEvents.trigger('error', params.message)
          response_handlers.sip_recieved.handle({
            status: "ko"
          });
          break;

        case "8":
          run_client_callback(weemo, 'onConnectionHandler', ["error", params.message]);
          apiEvents.trigger('error', params.message)
          debug("Cloud connection: Disconnected from the Cloud (err " + params.error + ")");
          throw "should not happen";

        default:
          var defaultError = "Error message : General error. Please contact support (err " + params.error + ")";
          apiEvents.trigger('error', defaultError)
          debug(defaultError);
      }

    }

  }
},
  get_result://driver
{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("get_result")[0];
    if (message) {
      var options = {};
      //return options;
    }
  }
},
  hold://driver
{
  parse: function(xmlDoc) {
    var holdNode = xmlDoc.getElementsByTagName("hold")[0];
    if (holdNode) {
      return true;
    }
  }
},
  inband_received://driver
{
  parse: function(xmlDoc) {
    var inbandreceived = xmlDoc.getElementsByTagName("inbandreceived")[0];
    if (inbandreceived) {
      if (inbandreceived.childNodes[0]) {
        return inbandreceived.childNodes[0].nodeValue;
      } else {
        return "";
      }
    }
  }
},
  kicked_received://driver
{
  parse: function(xmlDoc) {
    var kicked = xmlDoc.getElementsByTagName("kicked")[0];
    if (kicked) {
      var params = {};
      params.kickedName = kicked.getAttribute("displayname");
      params.kickedUrl = kicked.getAttribute("urlreferer");
      return params;
    }
  }
},
  meeting_point_attended:{
  parse: function(xmlDoc) {
    var meetingpointattended = xmlDoc.getElementsByTagName("meetingpointattended")[0];
    if (meetingpointattended) {
      var options = {};
      var statusNode = meetingpointattended.getAttribute("status");
      options.status = statusNode;
      var id = meetingpointattended.getElementsByTagName('meetingpointid')[0];
      if (id) {
        options.id = id.childNodes[0].nodeValue;
      }
      if (statusNode === "ok") {
        var request = meetingpointattended.getElementsByTagName("request")[0];
        if (request !== undefined && request !== null) {
          options.request = request.childNodes[0].nodeValue;
          if (options.request === "invited") {
            var displayname = meetingpointattended.getElementsByTagName('displayname')[0];
            if (displayname !== undefined && displayname !== null && displayname.childNodes[0] !== undefined) {
              options.displayName = displayname.childNodes[0].nodeValue

            }
            //request.
          }
        }


      } else {
        var error = meetingpointattended.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      }
      return options;
    }
  }
},
  meeting_point_controlled:{
  include: "xml_utils",
  parse: function(xmlDoc) {
    var meetingpointcontrolled = xmlDoc.getElementsByTagName("meetingpointcontrolled")[0];
    if (meetingpointcontrolled) {
      options = {};
      options.status = meetingpointcontrolled.getAttribute("status");
      var that = this;
      arrayForEach(['action', 'uid', 'mode', 'error'], function(name) {
        that.getChildrenIfExists(options, meetingpointcontrolled, name);
      });

      options.id = meetingpointcontrolled.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;

      return options;
    }


  }
},
  meeting_point_created:{
  include: "xml_utils",

  parse: function(xmlDoc) {
    var meetingpointcreated = xmlDoc.getElementsByTagName("meetingpointcreated")[0];
    if (meetingpointcreated) {

      var options = {};
      var statusNode = meetingpointcreated.getAttribute("status");
      options.status = statusNode
      if (statusNode === "ok") {
        options.id = meetingpointcreated.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;
        options.hostUrl = this.getKeyIfExists(meetingpointcreated, 'hosturl');
        options.attendeeUrl = this.getKeyIfExists(meetingpointcreated, 'attendeeurl');
      } else {
        error = meetingpointcreated.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }

      }
      return options;
    }
  }
},
  meeting_point_deleted:{

  parse: function(xmlDoc) {
    var meetingpointdeleted = xmlDoc.getElementsByTagName("meetingpointdeleted")[0];
    if (meetingpointdeleted) {
      var options = {};

      var statusNode = meetingpointdeleted.getAttribute("status");
      options.status = statusNode


      options.id = currentMeetingPointDeletedId;
      if (statusNode !== "ok") {
        var error = meetingpointdeleted.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      }
      return options;
    }
  }
},
  meeting_point_got:{
  include: "xml_utils",

  parse: function(xmlDoc) {
    var meetingpointgot = xmlDoc.getElementsByTagName("meetingpointgot")[0];
    if (meetingpointgot) {
      var options = {};
      var statusNode = meetingpointgot.getAttribute("status");
      options.status = statusNode
      if (statusNode === "ok") {
        options.id = meetingpointgot.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;
        options.hostUrl = this.getKeyIfExists(meetingpointgot, 'hosturl');
        options.attendeeUrl = this.getKeyIfExists(meetingpointgot, 'attendeeurl');
        options.type = meetingpointgot.getElementsByTagName('type')[0].childNodes[0].nodeValue;
        options.startDate = this.getKeyIfExists(meetingpointgot, 'startdate');
        options.mode = this.getKeyIfExists(meetingpointgot, 'mode');

        options.stopDate = this.getKeyIfExists(meetingpointgot, 'stopdate');
        options.location = this.getKeyIfExists(meetingpointgot, 'location');
        options.title = this.getKeyIfExists(meetingpointgot, 'title');
      } else {
        error = meetingpointgot.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }

      }
      return options;
    }
  }
},
  meeting_point_hosted:{
  parse: function(xmlDoc) {
    var meetingpointhosted = xmlDoc.getElementsByTagName("meetingpointhosted")[0];
    if (meetingpointhosted !== undefined && meetingpointhosted !== null) {
      var options = {};
      var mode;
      options.id = meetingpointhosted.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;
      var statusNode = meetingpointhosted.getAttribute("status");
      options.status = statusNode;
      mode = meetingpointhosted.getAttribute("mode");
      if (mode === '1') {
        options.callType = Rtcc.callType.ONE_TO_ONE;
      } else {
        options.callType = Rtcc.callType.N_TO_N;
      }
      if (statusNode !== "ok") {
        var error = meetingpointhosted.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }


      }
      return options;
    }
  }
},
  meeting_point_modified:{
  parse: function(xmlDoc) {
    var meetingpointmodified = xmlDoc.getElementsByTagName("meetingpointmodified")[0];
    if (meetingpointmodified) {
      var options = {};
      var statusNode = meetingpointmodified.getAttribute("status");
      options.status = statusNode
      options.id = meetingpointmodified.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;
      if (statusNode !== "ok") {
        var error = meetingpointmodified.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      }
      return options;
    }
  }
},
  meeting_point_requested:{
  parse: function(xmlDoc) {
    var meetingpointrequested = xmlDoc.getElementsByTagName("meetingpointrequested")[0];

    if (meetingpointrequested) {
      var options = {};
      options.id = meetingpointrequested.getElementsByTagName('meetingpointid')[0].childNodes[0].nodeValue;
      options.status = meetingpointrequested.getAttribute("status");
      var timestamp = meetingpointrequested.getElementsByTagName("timestamp")[0];
      if (timestamp) {
        options.timestamp = timestamp.childNodes[0].nodeValue;
      }
      if (options.status !== "ok") {
        var error = meetingpointrequested.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      } else {
        options.status = meetingpointrequested.getElementsByTagName('request')[0].childNodes[0].nodeValue;
        if (meetingpointrequested.getElementsByTagName('uid')[0] && meetingpointrequested.getElementsByTagName('uid')[0].childNodes[0]) {
          options.uid = meetingpointrequested.getElementsByTagName('uid')[0].childNodes[0].nodeValue;
        }
        if ((meetingpointrequested.getElementsByTagName('displayname')[0]) && (meetingpointrequested.getElementsByTagName('displayname')[0].childNodes[0])) {
          options.displayName = meetingpointrequested.getElementsByTagName('displayname')[0].childNodes[0].nodeValue;
        }

      }
      return options;

    }
  }
},
  message_received:{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("presencemessage")[0];
    if (message) {
      var options = {};
      options.uid = message.getAttribute("from");
      options.message_id = message.getAttribute("id");
      if (message.childNodes[0]) {
        options.message = message.childNodes[0].nodeValue;
      } else {
        options.message = "";
      }
      return options;
    }
  }
},
  permanent_meeting_point_got:{

  parse: function(xmlDoc) {
    var permanentmeetingpointgot = xmlDoc.getElementsByTagName("permanentmeetingpointgot")[0];
    if (permanentmeetingpointgot) {
      var options = {};
      var statusNode = permanentmeetingpointgot.getAttribute("status");
      options.status = statusNode
      if (statusNode === "ok") {
        if (permanentmeetingpointgot.getElementsByTagName('attendeeurl')[0].childNodes[0]) {
          options.attendeeUrl = permanentmeetingpointgot.getElementsByTagName('attendeeurl')[0].childNodes[0].nodeValue;
        }
      } else {
        error = permanentmeetingpointgot.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }

      }
      return options;
    }
  }
},
  preprocessor:{
  execute: function(xml) {
    var xmlDoc;
    if (window.DOMParser) {
      parser = new DOMParser();
      xmlDoc = parser.parseFromString(xml, "text/xml");
    } else { // Internet Explorer
      xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
      xmlDoc.async = false;
      xmlDoc.loadXML(xml);
    }
    return xmlDoc;
  }
},
  presence_burstupdate://driver
{
  include: ["driver_convert_presence_payload"],
  parse: function(data) {
    var presenceupdate = data.getElementsByTagName("presenceburstupdate")[0];
    if (presenceupdate) {
      return this.convertPresencePayload(presenceupdate);
    }
  }
},
  presence_received:{
  parse: function(xmlDoc) {
    var userregistered = xmlDoc.getElementsByTagName("userregistered")[0];
    if (userregistered) {
      var options = {};
      options.rosterlen = Number(userregistered.getAttribute("len"));
      options.status = userregistered.childNodes[0].nodeValue;
      if (options.status === "unregistered") {
        return "presenceNok";
      } else {
        return options;
      }
    }
  }
},
  presence_update://driver
{
  include: ["driver_convert_presence_payload"],
  parse: function(data) {
    var presenceupdate = data.getElementsByTagName("presenceupdate")[0];
    if (presenceupdate) {
      return this.convertPresencePayload(presenceupdate);
    }
  }
},
  presence_wholeroster:{
  include: 'driver_convert_chunked_presence_payload',
  parse: function(data) {
    var roster = data.getElementsByTagName("roster")[0];
    if (roster) {
      var options = {};

      options.length = Number(roster.getAttribute("len"));
      options.uid_array = this.convertPresencePayload(roster);
      return options;
    }
  }
},
  readyforauthentication_received://driver
{
  parse: function(xmlDoc) {
    var readyforauthentication = xmlDoc.getElementsByTagName("readyforauthentication")[0];
    if (readyforauthentication) {
      return true;
    }
  }
},
  roster_updated:{
  parse: function(data) {

    var rosterupdated = data.getElementsByTagName("rosterupdated")[0];
    if (rosterupdated) {
      var options = {};
      options.length = Number(rosterupdated.getAttribute("len"));
      options.updated = Number(rosterupdated.getAttribute("updated"));
      return options;
    }
  }
},
  set_received://driver
{
  parse: function(xmlDoc) {
    var set = xmlDoc.getElementsByTagName("set")[0];
    if (set) {
      var params = {};
      var displayNameSet = set.getAttribute("displayname");
      var versionSet = set.getAttribute("version");
      var statusSet = set.getAttribute("status");
      var callwindowDefaultPositionSet = set.getAttribute('callwindowdefaultposition');
      var domainStatusSet = set.getAttribute("domainstatus");
      var domainSet = set.getAttribute("domain");
      var profileSet = set.getAttribute("domainprofile");
      if (displayNameSet !== null) {
        params.name = "displayName";
        params.value = displayNameSet.decodeHTML();
      } else if (versionSet !== null) {
        params.name = "version";
        params.value = versionSet;
      } else if (statusSet !== null) {
        params.name = "status";
        params.value = parseInt(statusSet, 10);
        params.uid = set.getAttribute("uid");
      } else if (callwindowDefaultPositionSet !== null) {
        params.name = 'callWindowDefaultPosition';
        params.value = callwindowDefaultPositionSet;
      } else if (domainStatusSet !== null) {
        params.name = "domainstatus";
        params.value = parseInt(domainStatusSet, 10);
        params.domain = domainSet;
      } else if (profileSet !== null) {
        params.name = "domainprofile";
        params.value = parseInt(profileSet, 10);
      }
      return params;
    }
  }
},
  sip_message_received://driver
{
  parse: function(xmlDoc) {
    var message = xmlDoc.getElementsByTagName("message")[0];
    if (message) {
      options = {};
      var from_id = message.getAttribute("fromid");
      options.id = Number(from_id)
      var displayName = message.getAttribute("from");
      options.displayName = displayName;
      options.message = message.childNodes[0].nodeValue;
      return options;
    }
  }
},
  sip_recieved:{
  parse: function(xmlDoc) {
    var status = xmlDoc.getElementsByTagName("status")[0];
    if (status) {
      var sip = status.getElementsByTagName("sip")[0];
      if (sip) {
        if (sip.childNodes[0].nodeValue === "ok") {
          return {
            type: "driver",
            status: "ok"
          }
        } else {
          return {
            status: "nok"
          }
        }
      }
    }
  }
},
  six_digits_deleted://driver
{
  parse: function(xmlDoc) {
    var sixdigitsdeleted = xmlDoc.getElementsByTagName("sixdigitsdeleted")[0];
    if (sixdigitsdeleted) {
      options = {};
      statusNode = sixdigitsdeleted.getAttribute("status");
      options.status = statusNode;

      if (options.status === "ko") {
        var error = sixdigitsdeleted.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      }
      return options
    }

  }
},
  sixdigits_created://driver
{
  include: "xml_utils",
  parse: function(xmlDoc) {

    var sixdigitscreated = xmlDoc.getElementsByTagName("sixdigitscreated")[0];
    if (sixdigitscreated) {
      var options = {};
      options.status = sixdigitscreated.getAttribute("status");

      if (options.status === "ok") {
        options.sixdigits = this.getKeyIfExists(sixdigitscreated, 'sixdigits');
      } else {
        var error = sixdigitscreated.getElementsByTagName('error')[0];
        if (error) {
          options.error = error.childNodes[0].nodeValue;
        }
      }
      return options;
    }
  }
},
  verifieduser_received://driver
{
  parse: function(xmlDoc) {
    var verifieduser = xmlDoc.getElementsByTagName("verifieduser")[0];
    var type;
    if (verifieduser) {
      var params = {};
      var sixdigits = verifieduser.getAttribute('sixdigits');
      if (sixdigits) {
        params.sixdigits = sixdigits;
      }
      type = verifieduser.childNodes[0].nodeValue;
      if (type !== "ok" && type !== "loggedasotheruser") {
        var errorVerifiedNode = verifieduser.getElementsByTagName("error")[0];
        if (errorVerifiedNode !== undefined) {
          var error_code = errorVerifiedNode.getAttribute('code');
          if (error_code) {
            params.error = Number(error_code);
          }
          var message = errorVerifiedNode.getAttribute('details');
          if (message) {
            params.error_message = message;
          }
        }

      }
      return [type, params, "driver"]
    }
  }
},
  wait_list_retreived://driver
{
  convertPresencePayload: function(roster) {
    if (roster.childNodes.length === 0) {
      return [];
    } else {
      var child = roster.childNodes[0];
      roster.removeChild(child);
      return [{
        uid: child.childNodes[0].nodeValue,
        value: child.getAttribute("value"),
        mask: child.getAttribute("mask")
   }].concat(this.convertPresencePayload(roster))
    }
  },
  parse: function(data) {
    var waitlist = data.getElementsByTagName("acdwaitinglist")[0];
    if (waitlist) {
      var options = {};
      options.length = Number(waitlist.getAttribute("len"));
      options.uid_array = this.convertPresencePayload(waitlist);
      return options;
    }
  }
},
  wall_got:{
  include: "xml_utils",
  parse: function(xmlDoc) {

    var wallgot = xmlDoc.getElementsByTagName("wallgot")[0];
    if (wallgot) {
      var options = {};
      statusNode = wallgot.getAttribute("status");
      options.status = statusNode
      if (statusNode === "ok") {
        options.first_name = this.getKeyIfExists(wallgot, 'first_name');
        options.last_name = this.getKeyIfExists(wallgot, 'last_name');
        options.company_name = this.getKeyIfExists(wallgot, 'company_name');
        options.email = this.getKeyIfExists(wallgot, 'email');
        options.language = this.getKeyIfExists(wallgot, 'language');
        options.gender = this.getKeyIfExists(wallgot, 'gender');
        options.nickname = this.getKeyIfExists(wallgot, 'nickname');
        options.company_website = this.getKeyIfExists(wallgot, 'company_website');
        options.street_address = this.getKeyIfExists(wallgot, 'street_address');
        options.postal_code = this.getKeyIfExists(wallgot, 'postal_code');
        options.state = this.getKeyIfExists(wallgot, 'state');
        options.country = this.getKeyIfExists(wallgot, 'country');
        options.mobile = this.getKeyIfExists(wallgot, 'mobile');
        options.linkedin = this.getKeyIfExists(wallgot, 'linkedin');
        options.google_plus = this.getKeyIfExists(wallgot, 'google_plus');
        options.twitter = this.getKeyIfExists(wallgot, 'twitter');
        options.facebook = this.getKeyIfExists(wallgot, 'facebook');
      } else {
        var error = wallgot.getAttribute("error");

        if (error) {
          options.error = error
        }

      }
      return options;
    }
  }
},
  wall_updated:{
  parse: function(xmlDoc) {
    var wallupdated = xmlDoc.getElementsByTagName("wallupdated")[0];
    if (wallupdated) {
      var options = {};
      statusNode = wallupdated.getAttribute("status");
      options.status = statusNode
      if (statusNode !== "ok") {
        var error = wallupdated.getAttribute('error');
        if (error) {
          options.error = error
        }
      }
      return options;
    }
  }
}};;
var webrtc_parsers = {
  acknowledge_received:{
  parse: function(data) {
    if (data.cmd === "dc_ackrcvd") {
      var options = {}
      options.message_id = data.args[0];
      options.uid = data.args[1];
      options.status = data.args[2];
      return options;
    }
  }
},
  agent_or_queue_received://webrtc
{
  convertChunkedPresenceArray: function(pre_proc_array) {
    var slice = pre_proc_array.splice(0, 2)
    if (slice.length > 0) {
      return [{
        uid: slice[1],
        presence: slice[0]
      }].concat(this.convertChunkedPresenceArray(pre_proc_array));
    } else {
      return [];
    }
  },
  parse: function(data) {
    if (data.cmd === "acd_list") {
      var args = data.args;
      var options = {
        queue: {
          position: Number(args[0]),
          length: Number(args[1])
        },
        agents: {
          length: Number(args[2]),
          uid_array: this.convertChunkedPresenceArray(args.slice(3))
        }
      };
      return options;
    }

  }
},
  call_audio_received://webrtc
{
  parse: function(data) {
    if (data.cmd === "call_audio_received") {
      var args = data.args;
      var options = {};
      //return options;
    }

  }
},
  call_created://webrtc
{
  parse: function(data) {
    if (data.cmd === "createdcall") {
      var args = data.args;
      return args;
    }
  }
},
  call_status_received://webrtc
{
  parse: function(data) {

    if (data.cmd === "statuscall") {
      var args = data.args;
      var options = {};
      options.id = args[0];
      options.type = args[1];
      options.reason = args[2];

      return options;
    }

  }
},
  call_update_video_profile://webrtc
{
  parse: function(data) {
    if (data.cmd === "updatevideoprofile") {
      var params = data.args;
      var id = params[0];
      var callObjects = global_config.callObjects;
      var callObject = callObjects[id];
      if (callObject) {
        callObject._updateVideoProfile(params[1]);
      } else {
        debug("call " + id + "has already been destroyed");
      }
    }
  }
},
  call_video_received://webrtc
{
  parse: function(data) {
    if (data.cmd === "call_video_received") {
      var args = data.args;
      var options = {};
      //return options;
    }

  }
},
  client_call_requested://webrtc
{
  parse: function(data) {
    if (data.cmd === "acd_request") {
      var args = data.args;
      var options = {
        type: args[0],
        uid: args[1]
      };
      return options;
    }

  }
},
  conference_status://webrtc
{
  parse: function(data) {
    if (data.cmd === "conferencestatus") {
      var args = data.args;
      var options = {
        myId: args[2],
        isHost: args[3]
      };
      return options;
    }

  }
},
  error_received://webrtc
{
  parse: function(data) {
    if (data.cmd === "error") {
      debug("ERROR");
      debug(data.args);
    }
  }
},
  get_result://webrtc
{
  parse: function(data) {
    if (data.cmd === "get_result") {
      var args = data.args;
      return args;
    }
  }
},
  hold://webrtc
{
  parse: function(data) {
    if (data.cmd === "hold") {
      var args = data.args;
      var options = {};
      //return options;
    }

  }
},
  meeting_point_attended:{
  parse: function(data) {
    if (data.cmd === "meetingpointattended") {
      var args = data.args;
      var options = {};
      options.status = args[0]
      options.id = args[1];
      if (args[0] === "ok") {
        options.request = args[2]
        if (args[2] === "invited") {
          options.displayName = args[4]
        }

        if (args[5]) {
          options.confHash = args[5];
        }
      } else {
        options.error = args[2]
      }
      return options;
    }
  }
},
  meeting_point_controlled:{
  parse: function(data) {
    if (data.cmd === "meetingpointcontrolled") {
      var options = {};
      var args = data.args;
      options.status = args[0];
      options.id = args[1];
      options.action = args[2];
      options.uid = args[3];

      if (options.status !== 'ok') {
        options.error = args[5];
      }
      return options;
    }
  }
},
  meeting_point_created:{
  parse: function(data) {
    if (data.cmd === "meetingpointcreated") {
      var options = {}
      options.status = data.args[0];

      if (options.status === "ok") {
        options.id = data.args[1];
        options.hostUrl = data.args[2]
        options.attendeeUrl = data.args[3];
      } else {
        options.error = data.args[1];
      }
      return options;
    }
  }
},
  meeting_point_deleted:{
  parse: function(data) {

    if (data.cmd === "meetingpointdeleted") {
      var args = data.args;
      var options = {};
      options.status = args[0];
      options.id = currentMeetingPointDeletedId;
      if (options.status !== "ok") {
        options.error = args[2];
      }
      return options;
    }
  }
},
  meeting_point_got:{
  parse: function(data) {
    if (data.cmd === "meetingpointgot") {
      var options = {};
      var args = data.args;
      options.id = args[1];
      options.status = args[0];
      if (args[0] === "ok") {
        options.hostUrl = args[7];
        options.attendeeUrl = args[8];
        options.mode = args[9];

        options.type = args[2];
        options.startDate = args[3];
        options.stopDate = args[4];
        options.location = args[6];
        options.title = args[5];
      } else {
        options.error = args[2];
      }
      return options;
    }
  }
},
  meeting_point_hosted:{
  parse: function(data) {
    if (data.cmd === "meetingpointhosted") {
      var options = {}
      var args = data.args;
      options.status = args[0];
      options.id = args[1];
      options.callType = args[2];
      if (args[0] !== "ok") {
        options.error = args[2];
      }
      return options;
    }
  }
},
  meeting_point_modified:{
  parse: function(data) {
    if (data.cmd === "meetingpointmodified") {
      var options = {};
      var args = data.args;
      options.status = args[0]
      options.id = args[1]
      if (args[0] === "ok") {
        options.hostUrl = args[2];
        options.attendeeUrl = args[3];

      } else {
        options.error = args[2];
      }
      return options;
    }
  }
},
  meeting_point_requested:{
  parse: function(data) {
    if (data.cmd === "meetingpointrequested") {
      var options = {};
      var args = data.args;
      options.id = args[1];
      if (args[0] === "ok") {
        options.status = args[2];
        options.uid = args[3];
        options.displayName = args[4];
      } else {
        options.status = args[0];
        options.error = args[2];
      }
      return options;
    }
  }
},
  message_received:{
  parse: function(data) {
    if (data.cmd === "dc_send") {
      var options = {}
      options.message_id = data.args[0];
      options.uid = data.args[1];
      options.message = data.args[2];
      return options;
    }
  }
},
  participant_list://webrtc
{
  parse: function(data) {
    if (data.cmd === "plist") {
      var params = data.args;
      var callId = params.shift();

      //convert to good format:
      var pList = {
        participants: []
      };

      for (var i = 0; i < params.length; i++) {
        params[i].displayName = params[i].name;
        delete params[i].name;
        params[i].id = params[i].pid;
        delete params[i].pid;
        if (params[i].host) {
          delete params[i].host;
          pList.hostId = params[i].id;
        }
        pList.participants.push(params[i]);
      }


      global_config.callObjects[callId]._updateParticipantList(pList);
    }
  }
},
  permanent_meeting_point_got:{
	  parse: function(data) {
	    if (data.cmd === "permanentmeetingpointgot") {
	      var options = {};
	      var args = data.args;
	      options.status = args[0];
	      if (args[0] === "ok") {
	        options.attendeeUrl = args[1];
	      } else {
	        options.error = args[1];

	      }
	      return options;
	    }
	  }
	},
  pong://webrtc
{
  parse: function(data) {
    if (data.cmd === "pong") {
      vent.trigger('pong');
      return true;
    }
  }

},
  preprocessor:{
  execute: function(json_string) {
    try {
      return JSON.parse(json_string);
    } catch (error) {
      debug("error parsing json: " + json_string);
      debug(error.stack);
    }
  }
},
  presence_burstupdate://webrtc
{
  include: ["webrtc_convert_presence_payload"],
  parse: function(data) {
    if (data.cmd === "presence_burstupdate") {
      return this.convertPresencePayload(data.args)
    }
  }
},
  presence_received:{
  parse: function(data) {
    if (data.cmd === "user_registered") {
      return {
        status: data.args[0],
        rosterlen: data.args[1]
      }
    } else if (data.cmd === "user_unregistered") {
      return "presenceNok";
    }
  }
},
  presence_update:{
  include: ["webrtc_convert_presence_payload"],

  parse: function(data) {
    if (data.cmd === "presence_update") {
      return this.convertPresencePayload(data.args)
    }
  }
},
  presence_wholeroster:{
  include: 'webrtc_convert_chuncked_presence_payload',
  parse: function(data) {
    if (data.cmd === "presence_wholeroster") {
      var options = {};
      options.length = Number(data.args[0]);
      options.uid_array = this.convertChunkedPresenceArray(data.args.slice(1));
      return options;
    }
  }
},
  roster_updated:{
  parse: function(data) {
    if (data.cmd === "roster_updated") {
      return {
        length: Number(data.args[0]),
        updated: Number(data.args[1])
      }

    }
  }
},
  sip_message_received://webrtc
{
  parse: function(data) {
    if (data.cmd === "message") {
      var args = data.args;
      var options = {};
      options.id = Number(data.args[1]);
      options.displayName = data.args[0];
      options.message = data.args[2];
      return options;
    }
  }
},
  sip_recieved:{
  parse: function(data) {
    if (data.cmd === "status") {
      if (data.args[0] === "sip") {
        return {
          type: "webrtc",
          status: data.args[1]
        }
      }
    }
  }
},
  six_digits_deleted://webrtc
{
  parse: function(data) {
    if (data.cmd === "sixdigitsdeleted") {
      var args = data.args;
      return data.args;
      //return options;
    }

  }
},
  sixdigits_created://webrtc
{
  parse: function(data) {
    if (data.cmd === "sixdigitscreated") {
      var args = data.args;
      if (args.digits) {
        args.sixdigits = args.digits;
        delete args.digits;
      }
      return args;
    }

  }
},
  updatemedia://webrtc
{
  parse: function(data) {
    if (data.cmd === "updatemedia") {
      var params = data.args;
      var id = params[0];
      var callObjects = global_config.callObjects;
      var callObject = callObjects[id];
      if (callObject) {
        callObject._updateMedia(params);
      } else {
        debug("call " + id + "has already been destroyed");
      }
    }
  }
},
  verifieduser_received://webrtc
{
  parse: function(params) {
    if (params.cmd === "verifieduser") {

      var type;
      var options = {};
      type = params.args[0];

      if (type !== "ok") {
        options.error = Number(params.args[1]);
        options.error_message = params.args[2];
      } else if (params.args[1]) {
        options.sixdigits = params.args[1];
      }
      return [type, options, "webrtc"]
    }
  }
},
  wait_list_retreived:{
  convertChunkedPresenceArray: function(pre_proc_array) {
    var slice = pre_proc_array.splice(0, 3)
    if (slice.length > 0) {
      return [{
        uid: slice[2],
        value: slice[0],
        mask: slice[1]
      }].concat(this.convertChunkedPresenceArray(pre_proc_array));
    } else {
      return [];
    }
  },
  parse: function(data) {
    if (data.cmd === "acd_waitingqueue") {
      var options = {};
      options.length = Number(data.args[0]);
      options.uid_array = this.convertChunkedPresenceArray(data.args.slice(1));
      return options;
    }
  }
},
  wall_got:{
  parse: function(data) {
    if (data.cmd === "wallgot") {
      return data.args[0];
    }
  }
},
  wall_updated:{
  parse: function(data) {
    if (data.cmd === "wallupdated") {
      return data.args[0];
    }
  }
}};;
var response_handlers = {
  acknowledge_received:{
	  handle: function(params) {
	    run_client_callback(weemo, "onAcknowledgeReceived", [params.message_id, params.uid, params.status]);
	    apiEvents.trigger('message.acknowledge', params.message_id, params.uid, params.status);
	  }
	},
  agent_or_queue_received:{
  current_agent_queue_being_loaded: [],
  handle: function(params) {
    if (params.queue.position > 0) {
      run_client_callback(weemo, 'onCallDistributorQueueUpdate', [params.queue]);
      apiEvents.trigger('calldistributor.queue.update', params.queue);
    } else {
      this.current_agent_queue_being_loaded = this.current_agent_queue_being_loaded.concat(params.agents.uid_array);
      if (this.current_agent_queue_being_loaded.length === params.agents.length) {
        apiEvents.trigger('calldistributor.agent.available', this.current_agent_queue_being_loaded);
        run_client_callback(weemo, 'onCallDistributorAgentAvailable', [this.current_agent_queue_being_loaded]);
        this.current_agent_queue_being_loaded = [];
      }

    }
  }
},
  audio_receieved:{
  handle: function(status) {
    if (status === "ok") {
      run_client_callback(weemo, 'onConnectionHandler', ['audioOk', 0]);
      apiEvents.trigger('audio.ok')
    } else {
      run_client_callback(weemo, 'onConnectionHandler', ['audioNok', 0]);
      apiEvents.trigger('audio.ko')
    }
  }
},
  call_audio_received:{
  handle: function(params) {
    run_client_callback(weemo, 'onTest', ['audioreceived']);
    apiEvents.trigger('test.audioreceived')
  }
},
  call_created:{
  handle: function(params) {
    weemo.requests.run("call_created", [params]);
  }
},
  call_status_received:{
  current_share_list: [],
  handle: function(params) {
    var callObject = global_config.callObjects[params.id];
    if (!callObject) {
      debug("call " + params.id + "has already been destroyed");
      return;
    }

    if (params.conference && global_config.plugin) {
      if (params.conference.floor) {
        globalVars.webRtcUi.setPassiveVideoBoxes(params.conference.floor);
      } else if (params.conference.participantList) {
        globalVars.webRtcUi.setParticipantList(params.conference.participantList);
      }
    }

    if (params.type === "share_local_list") {
      this.current_share_list.push({
        id: params.item_id,
        name: params.item_name
      });
      if (this.current_share_list.length === params.item_number) {
        var oldParams = params;
        params = {};
        params.id = oldParams.id;
        params.type = oldParams.type;
        params.status = this.current_share_list;
        this.current_share_list = [];
      } else {
        return;
      }
    }
    callObject._updateCallStatus(params);
    if (params.status === "terminated") {
      global_config.callObjects[params.id].terminated = true;
      delete global_config.callObjects[params.id];
    }
  }
},
  call_video_received:{
  handle: function(params) {
    run_client_callback(weemo, 'onTest', ['videoreceived']);
    apiEvents.trigger('test.videoreceived')
  }
},
  client_call_requested:{
  client_requests: {},
  handle: function(params) {
    this.client_requests[params.uid] = new ClientCallRequest(params.uid);

    if (params.type === 'canceled') {
      this.client_requests[params.uid].status = 'canceled';
    }
    run_client_callback(weemo, 'onCallDistributorClientCallRequest', [this.client_requests[params.uid]]);
    apiEvents.trigger('calldistributor.request', this.client_requests[params.uid]);
  }
},
  conference_status:{
  handle: function(params) {
    if (globalVars.webRtcUi.setWelcome)
      globalVars.webRtcUi.setWelcome(params.myId, params.isHost)
  }
},
  dropped_received:{
  handle: function(params) {
    modeFacade.websock.close();
    run_client_callback(weemo, 'onConnectionHandler', ['dropped', null]);
    apiEvents.trigger('cloud.drop')
  }
},
  get_result:{
  handle: function(params) {
    var return_obj = {};
    if (params[0] === "displayname") {
      return_obj.name = "displayName";
      return_obj.value = params[1];
      global_config.displayName = params[1];
    } else if (params[0] === "status") {
      return_obj.name = "status";
      return_obj.uid = params[1];
      return_obj.value = Number(params[2]);
    }
    run_client_callback(weemo, 'onGetHandler', [return_obj.name, return_obj]);
    apiEvents.trigger('get.' + return_obj.name.toLowerCase(), return_obj);
    apiEvents.trigger('get', return_obj.name, return_obj);
  }
},
  hold:{
  handle: function(params) {
    run_client_callback(weemo, 'onConnectionHandler', ['loggedonotherdevice', 0]);
    apiEvents.trigger('cloud.alreadyconnected')
  }
},
  inband_received:{
  handle: function(message) {
    run_client_callback(weemo, 'onInbandMessageReceived', [message]);
    apiEvents.trigger('message.inband', message);
    if (globalVars.call) {
      globalVars.call.trigger('inband.message.receive', message);
    } else {
      debug("No call established");
    }
  }
},
  kicked_received:{
  handle: function(params) {
    modeFacade.websock.close();
  }
},
  meeting_point_attended:{
	  handle: function(params) {
	    var action;
	    if (params.status === "ok") {
	      if (params.request === "invited") {
	        meetingPointAttendees[params.id] = new MeetingPointAttendee(params.id, params.displayName);
	        meetingPointAttendees[params.id].status = "waitingForApproval";
	        run_client_callback(weemo, 'onConfCallHandler', ["attendeeInvited", meetingPointAttendees[params.id]]);
	        apiEvents.trigger('meetingpoint.attendee.invite', meetingPointAttendees[params.id]);
	      } else {
	        var attendee = meetingPointAttendees[params.id];
	        if (attendee) {
	          attendee.status = "ok";
	          if (params.request === "pending") {
	            attendee.status = "waitingForApproval";
	            action = 'attendeePending';
	            apiEvents.trigger('meetingpoint.attendee.pending', attendee)
	          } else if (params.request === "accepted") {
	            if (params.confHash) {
	              attendee.confHash = params.confHash;
	            }
	            attendee.status = "accepted";
	            if (global_config.standAlone !== true) {
	              weemo.createCall(params.id, "attendee", 'conference');
	            }
	            action = 'attendeeAccepted';
	            apiEvents.trigger('meetingpoint.attendee.accept', attendee)
	          } else if (params.request === 'denied') {
	            attendee.status = params.request;
	            action = 'attendeeDenied';
	            apiEvents.trigger('meetingpoint.attendee.deny', attendee)
	          } else if (params.request === 'meetingcancelled') {
	            action = 'meetingCancelled';
	            apiEvents.trigger('meetingpoint.cancel')
	          } else {
	            throw 'Unexpected request parameter: ' + params.request;
	          }
	          return run_client_callback(weemo, 'onConfCallHandler', [action, attendee]);
	        } else {
	          debug('no meeting point created', {
	            show_on_debug_level: 3
	          });
	        }
	      }
	    } else {
	      // this solution is better but it requires hte meetingpointid to be brought down.
	      //meetingPointAttendees[params.id].status = "error";
	      // meetingPointAttendees[params.id].error = params.error;
	      // meetingPointAttendees[params.id].status = "error";
	      // meetingPointAttendees[params.id].error = params.error;

	      //FOR a quick-fix don't depend on currently optional params.id, in the future, fix back.
	      //https://weemocloud.atlassian.net/browse/JS-62
	      apiEvents.trigger('meetingpoint.attendee.error', params.id, params.error)
	      return run_client_callback(weemo, 'onConfCallHandler', ['attendeeError', {
	        status: "error",
	        error: params.error,
	        id: params.id
    }]);
	    }
	  }
	},
  meeting_point_controlled:{
  handle: function(params) {
    //TODO change to invite
    if (params.action === 'invite') {
      if (params.status === "ok") {
        params.status = "waitingForApproval";
        //TODO When UIDS are available in response:
        //createdMeetingPoints[params.id].attendees[params.uid].status = "waitingForApproval";
        //run_client_callback(weemo, 'onConfCallHandler', ["joinRequestSent", createdMeetingPoints[params.id].attendees[params.uid]]);
      }
      run_client_callback(weemo, 'onConfCallHandler', ["joinRequestSent", params]);

      if (params.status === 'ko') {
        apiEvents.trigger('error', params.error)
        apiEvents.trigger('meetingpoint.joinrequest.error', params.id, params, params.error)
      } else {
        apiEvents.trigger('meetingpoint.joinrequest.send', params.id, params)
      }
    } else if (params.action === 'accept') {
      if (createdMeetingPoints[params.id] && createdMeetingPoints[params.id].attendees[params.uid]) {
        createdMeetingPoints[params.id].attendees[params.uid].status = "accepted";
      }
    } else if (params.action === 'deny') {
      if (createdMeetingPoints[params.id] && createdMeetingPoints[params.id].attendees[params.uid]) {
        createdMeetingPoints[params.id].attendees[params.uid].status = "denied";
      } else if (joinRequestNotifications[params.id] && joinRequestNotifications[params.id][params.uid]) {
        joinRequestNotifications[params.id][params.uid].status = "denied";
      }


    }
  }
},
  meeting_point_created:{
  handle: function(params) {
    if (params.status === "ok") {
      global_config.meetingPointBeingCreated.id = params.id;
      global_config.meetingPointBeingCreated.status = "saved";
      global_config.meetingPointBeingCreated.hostUrl = params.hostUrl;
      global_config.meetingPointBeingCreated.attendeeUrl = params.attendeeUrl;
      createdMeetingPoints[params.id] = global_config.meetingPointBeingCreated;
      run_client_callback(weemo, 'onConfCallHandler', ["meetingPointCreated", createdMeetingPoints[params.id]]);
      apiEvents.trigger('meetingpoint.create.success', createdMeetingPoints[params.id])
    } else {
      global_config.meetingPointBeingCreated.status = "errorSaving";
      global_config.meetingPointBeingCreated.error = params.error;
      var errored_object = global_config.meetingPointBeingCreated;
      run_client_callback(weemo, 'onConfCallHandler', ["meetingPointCreated", errored_object]);
      apiEvents.trigger('error', params.error);
      apiEvents.trigger('meetingpoint.create.error', errored_object)
    }

  }
},
  meeting_point_deleted:{
	  handle: function(params) {
	    var return_obj = {};
	    if (params.status === "ok") {
	      return_obj.status = "deleted";
	      apiEvents.trigger('meetingpoint.delete.success', params.id)
	    } else {
	      return_obj.status = "errorDeleting";
	      return_obj.error = params.error;
	      apiEvents.trigger('error', params.error)
	      apiEvents.trigger('meetingpoint.delete.error', params.id, params.error)
	    }
	    run_client_callback(weemo, 'onConfCallHandler', ["meetingPointDeleted", return_obj]);

	  }
	},
  meeting_point_got:{
  handle: function(params) {
    if (params.status === "ok") {
      params.status = "saved";
      createdMeetingPoints[params.id] = new MeetingPointHost(params.type, params);
      run_client_callback(weemo, 'onConfCallHandler', ["meetingPointGot", createdMeetingPoints[params.id]]);
      apiEvents.trigger('meetingpoint.get.success', createdMeetingPoints[params.id])
    } else {
      run_client_callback(weemo, 'onConfCallHandler', ["meetingPointGot", params]);
      apiEvents.trigger('error', params.error)
      apiEvents.trigger('meetingpoint.get.error', params.error)
    }
  }
},
  meeting_point_hosted:{
	  handle: function(params) {
	    if (params.callType) {
	      createdMeetingPoints[params.id].callType = params.callType
	    }

	    if (params.status === "ok") {
	      createdMeetingPoints[params.id].status = "started";
	      if (params.callType !== Rtcc.callType.ONE_TO_ONE) {
	        weemo.createCall(params.id, "host", 'conference');
	      }
	      apiEvents.trigger('meetinpoint.host.success', createdMeetingPoints[params.id])
	    } else {
	      createdMeetingPoints[params.id].status = "startFailed";
	      createdMeetingPoints[params.id].error = params.error;
	      apiEvents.trigger('error', params.error)
	      apiEvents.trigger('meetingpoint.host.error', params.id, params.error)
	    }
	    run_client_callback(weemo, 'onConfCallHandler', ["meetingPointHosted", createdMeetingPoints[params.id]]);

	  }
	},
  meeting_point_modified:{
	  handle: function(params) {
	    if (params.status === "ok") {
	      createdMeetingPoints[params.id].modify_success_callback();
	      apiEvents.trigger('meetingpoint.modify.success', createdMeetingPoints[params.id])
	    } else {
	      createdMeetingPoints[params.id].status = "errorModifing";
	      createdMeetingPoints[params.id].error = params.error;
	      createdMeetingPoints[params.id].modify_failure_callback();
	      apiEvents.trigger('error', params.error)
	      apiEvents.trigger('meetingpoint.modify.error', params.id, params.error)
	    }
	    run_client_callback(weemo, 'onConfCallHandler', ["meetingPointModified", createdMeetingPoints[params.id]]);

	  }
	},
  meeting_point_requested:{
	  handle: function(params) {
	    var mpi = createdMeetingPoints[params.id];
	    if (params.status === "requesttoattend") {
	      if (mpi) {
	        //request has to do with our meeting point
	        attendee = new Attendee(params.id, params.uid, params.displayName);
	        if (params.timestamp) {
	          attendee.timestamp = params.timestamp;
	        } else {
	          attendee.timestamp = Math.round(new Date().valueOf() / 1000);
	        }
	        mpi.attendees[params.uid] = attendee
	        run_client_callback(weemo, 'onConfCallHandler', ["joinRequest", attendee]);
	        apiEvents.trigger('meetingpoint.joinrequest.new', attendee)
	      } else {
	        var error = 'The meeting point ' + params.id + ' does not exists in current context!';
	        debug(error)
	        apiEvents.trigger('error', error)
	        apiEvents.trigger('meetingpoint.joinrequest.error', params.id, error)
	      }
	    } else if (params.status === "accepted") {
	      mpi.attendees[params.uid].status = "ok";
	      mpi.attendees[params.uid].displayName = params.displayName;
	      mpi.attendees[params.uid].timestamp = params.timestamp;
	      run_client_callback(weemo, 'onConfCallHandler', ["joinRequestAccepted", mpi.attendees[params.uid]]);
	      apiEvents.trigger('meetingpoint.joinrequest.accept', mpi.attendees[params.uid])
	    } else if (params.status === "denied") {
	      mpi.attendees[params.uid].status = "nok";
	      mpi.attendees[params.uid].displayName = params.displayName;
	      mpi.attendees[params.uid].timestamp = params.timestamp;
	      run_client_callback(weemo, 'onConfCallHandler', ["joinRequestDenied", mpi.attendees[params.uid]]);
	      apiEvents.trigger('meetingpoint.joinrequest.deny', mpi.attendees[params.uid])
	    } else if (params.status === "notification") {
	      var timestamp = params.timestamp;
	      if (!timestamp) {
	        timestamp = Math.round(new Date().valueOf() / 1000);
	      }
	      var notification = new JoinRequestNotification({
	        id: params.id,
	        uid: params.uid,
	        timestamp: timestamp,
	        displayName: params.displayName
	      })
	      if (!joinRequestNotifications[params.id]) {
	        joinRequestNotifications[params.id] = {}
	      }
	      joinRequestNotifications[params.id][params.uid] = notification;

	      run_client_callback(weemo, 'onConfCallHandler', ["joinRequestNotification", notification]);
	      apiEvents.trigger('meetingpoint.notification', notification)
	    } else if (params.status === 'requestcancelled') {
	      var requestCancelled = {
	        id: params.id,
	        uid: params.uid,
	        displayName: params.displayName
	      };
	      delete mpi.attendees[params.uid];
	      run_client_callback(weemo, 'onConfCallHandler', ["joinRequestCancelled", requestCancelled]);
	      apiEvents.trigger('meetingpoint.joinrequest.cancel', requestCancelled)
	    }
	  }
	},
  message_received:{
	  handle: function(params) {
	    run_client_callback(weemo, "onMessageReceived", [params.message_id, params.uid, params.message]);
	    apiEvents.trigger('message.receive', params.message_id, params.uid, params.message)
	  }
	},
  participant_list:{
  handle: function(params) {}
},
  permanent_meeting_point_got:{
	  handle: function(params) {
	    run_client_callback(weemo, 'onConfCallHandler', ["permanentMeetingPointGot", params]);

	  }
	},
  presence_burstupdate:{
  handle: function(params) {
    run_client_callback(weemo, 'onBurstUpdate', [params]);
    apiEvents.trigger('presence.burstupdate', params)
  }
},
  presence_received:{
  handle: function(data) {
    if (data === "presenceNok") {
      run_client_callback(weemo, 'onConnectionHandler', ['presenceNok']);
      apiEvents.trigger('presence.ko')
      globalVars.presence_state = Rtcc.PRESENCE_STATES.NOK;
    } else {
      globalVars.presence_state = Rtcc.PRESENCE_STATES.OK;
      if ((Number(data.status) === 32) || data.status === "alreadyregistered") {
        run_client_callback(weemo, 'onConnectionHandler', ['presenceOkAlreadyRegistered', data.rosterlen]);
        apiEvents.trigger('presence.alreadyregistered')
        apiEvents.trigger('presence.ok', data.rosterlen)
      } else if ((Number(data.status) === 16) || data.status === "newuser") {
        run_client_callback(weemo, 'onConnectionHandler', ['presenceOkNewUser', data.rosterlen]);
        apiEvents.trigger('presence.newuser')
        apiEvents.trigger('presence.ok', data.rosterlen)

      }
    }
  }
},
  presence_update:{
	  handle: function(presence_array) {
	    run_client_callback(weemo, 'onPresenceUpdate', [presence_array]);
	    apiEvents.trigger('presence.update', presence_array)
	  }
	},
  presence_wholeroster:{
  current_roster_being_loaded: [],
  handle: function(options) {
    this.current_roster_being_loaded = this.current_roster_being_loaded.concat(options.uid_array);
    if (this.current_roster_being_loaded.length === options.length) {
      run_client_callback(weemo, 'onRosterRetrieved', [this.current_roster_being_loaded]);
      apiEvents.trigger('presence.roster.retrieve', this.current_roster_being_loaded)
      this.current_roster_being_loaded = [];
    }
  }
},
  readyforauthentication_received:{
  handle: function(params) {
    clearTimeout(globalVars.timeout.pluginConnect);
    actions.authenticate(global_config);
  }
},
  roster_updated:{
  handle: function(data) {
    run_client_callback(weemo, 'onRosterUpdated', ["ok", data]);
    apiEvents.trigger('presence.roster.update', data.updated, data.length)
  }
},
  set_received:{
  handle: function(params) {
    if (params.name === "displayName") {
      global_config.displayName = params.value;
    }
    run_client_callback(weemo, 'onGetHandler', [params.name, params]);
    apiEvents.trigger('get', params)
    var value;
    if (params.uid) {
      value = {
        uid: params.uid,
        value: params.value
      }
    } else if (params.domain) {
      value = {
        domain: params.domain,
        value: params.value
      }
    } else {
      value = params.value
    }

    apiEvents.trigger('get.' + params.name.toLowerCase(), value)
  }
},
  sip_message_received:{
  handle: function(options) {
    var message = options.message.substr(1);
    if (!arrayContains(global_config.non_uid_ids_for_sending_messages, options.id)) {
      global_config.non_uid_ids_for_sending_messages.push(options.id);
    }
    var aMyUTF8Output = base64DecToArr(message);
    var sMyOutput = UTF8ArrToStr(aMyUTF8Output);
    run_client_callback(weemo, 'onDataChannelMessageReceived', [options.id, options.displayName, sMyOutput]);
    apiEvents.trigger('message.datachannel', options.id, options.displayName, sMyOutput)
  }
},
  sip_recieved:{
  handle: function(data) {
    var callObjects = global_config.callObjects;
    if (data.status === "ok") {
      globalVars.state = Rtcc.STATES.SIP_OK;
      vent.trigger("sip_ok_" + data.type);
      if (!global_config.sixDigitNoCall) {
        if (globalVars.sixDigitsCallMode === "1") {
          weemo.createCall('ignoreduid', 'sixdigits', 'Call Starting');
        } else if (globalVars.sixDigitsCallMode === "n") {
          weemo.joinConfCall('sixdigits_meetingpointid');
        }
      }
      run_client_callback(weemo, 'onConnectionHandler', ['sipOk', 0]);
      apiEvents.trigger('cloud.sip.ok');
      if (data.type === "webrtc") {
        if (weemo.isShareExtensionLoaded()) {
          apiEvents.trigger('chrome.screenshare.loaded');
        } else {
          apiEvents.trigger('chrome.screenshare.missing', globalVars.screenShareExtentionUrl);
        }
      }
    } else {
      globalVars.state = Rtcc.STATES.SIP_NOK;
      objectForEach(callObjects, function(k, v) {
        v.hangup();
      })
      global_config.callObjects = {};
      run_client_callback(weemo, 'onConnectionHandler', ['sipNok', 0]);
      apiEvents.trigger('cloud.sip.ko');
    }
  }
},
  six_digits_deleted:{
  handle: function(params) {
    run_client_callback(weemo, 'onSixDigitsDeleted', [params]);
    if (params.status === 'ok') {
      apiEvents.trigger('sixdigits.delete.success')
    } else {
      if (params.error)
        apiEvents.trigger('sixdigits.delete.error', params.error)
      else
        apiEvents.trigger('sixdigits.delete.error')
    }
  }
},
  sixdigits_created:{
  handle: function(params) {
    run_client_callback(weemo, 'onSixDigitsCreated', [params]);
    if (params.status === 'ok') {
      apiEvents.trigger('sixdigits.create.success', params.sixdigits)
    } else {
      if (params.error)
        apiEvents.trigger('sixdigits.create.error', params.error)
      else
        apiEvents.trigger('sixdigits.create.error')
    }
  }
},
  verifieduser_received:{
  handle: function(options) {
    var params = options[1];
    if (options[0] === "loggedasotheruser") {
      run_client_callback(weemo, 'onConnectionHandler', ["loggedasotheruser", 0]);
      apiEvents.trigger('cloud.loggedasotheruser')
    } else if (options[0] === "ok") {
      globalVars.state = Rtcc.STATES.VERIFIED_USER_OK;
      weemo.setDisplayName(global_config.displayName);

      if (params.sixdigits) {
        globalVars.sixDigitsCallMode = params.sixdigits;
      }
      vent.trigger('verifieduser_ok_' + options[2]);
      run_client_callback(weemo, 'onConnectionHandler', ['authenticated', 0]);
      apiEvents.trigger('cloud.authenticate.success');
      if (options[2] === "webrtc") {
        var msg = {
          "cmd": "configdetails",
          "args": [
            global_config.os + " " + global_config.osVersion,
            "",
            "",
            "",
            global_config.version,
            global_config.browser + " " + global_config.browserVersion,
            document.location.href,
            String(modeFacade.latency),
            modeFacade.localAddress,
            global_config.hap
          ]
        };
        modeFacade.send(msg);
      }
    } else {
      globalVars.state = Rtcc.STATES.VERIFIED_USER_NOK;
      if (options[2] === "driver") {
        run_client_callback(weemo, 'onConnectionHandler', ["unauthenticated", 0]);
      }

      if (params.error_message && params.error) {
        apiEvents.trigger('error', params.error, params.error_message);
        apiEvents.trigger('cloud.authenticate.error', params.error, params.error_message);
        run_client_callback(weemo, 'onConnectionHandler', ["error", params.error, params.error_message]);
      } else if (params.error) {
        apiEvents.trigger('error', params.error)
        apiEvents.trigger('cloud.authenticate.error', params.error)
        run_client_callback(weemo, 'onConnectionHandler', ["error", params.error]);

      } else {
        apiEvents.trigger('error')
        apiEvents.trigger('cloud.authenticate.error')
        run_client_callback(weemo, 'onConnectionHandler', ["error"]);
      }

    }
  }
},
  wait_list_retreived:{
  current_waitlist_being_loaded: [],
  handle: function(options) {
    this.current_waitlist_being_loaded = this.current_waitlist_being_loaded.concat(options.uid_array);
    if (this.current_waitlist_being_loaded.length === options.length) {
      apiEvents.trigger('calldistributor.waitlist.retrieve', this.current_waitlist_being_loaded);
      run_client_callback(weemo, 'onWaitListRetrieved', [this.current_waitlist_being_loaded]);
      this.current_waitlist_being_loaded = [];
    }
  }
},
  wall_got:{
	  handle: function(params) {
	    run_client_callback(weemo, 'onConfCallHandler', ["wallsettings", params]);
	    if (params.status === 'ok') {
	      var res = clone(params)
	      delete res.status;
	      apiEvents.trigger('wallsettings.get.success', res)
	    } else
	      apiEvents.trigger('wallsettings.get.error', params.error)
	  }
	},
  wall_updated:{
  handle: function(params) {
    run_client_callback(weemo, 'onConfCallHandler', ["wallsettingsupdated", params]);
    if (params.status === 'ok') {
      apiEvents.trigger('wallsettings.update.success')
    } else
      apiEvents.trigger('wallsettings.update.error', params.error)
  }
}};;
var shared = {
  allowed_after_connected:{
  allowed: function() {
    return (globalVars.state >= Rtcc.STATES.CONNECTED_TO_FACADE)
  }
},
  allowed_after_presence_ok:{
  allowed: function() {
    return (globalVars.presence_state >= Rtcc.PRESENCE_STATES.OK)
  }
},
  allowed_after_sip_ok:{
  allowed: function() {
    return (globalVars.state >= Rtcc.STATES.SIP_OK)
  }
},
  allowed_after_verified_user_ok:{
  allowed: function() {
    return (globalVars.state >= Rtcc.STATES.VERIFIED_USER_OK)
  }
},
  chunckable:{
  getNextChunk: function(uid_array, request_size) {
    var uid_array_clone = uid_array.slice(0);
    if (uid_array_clone.length > 0) {
      return {
        next: uid_array_clone.splice(0, request_size),
        remainder: uid_array_clone
      }
    } else {
      return {
        next: false,
        remainder: false
      }
    }
  }
},
  driver_convert_chunked_presence_payload:{
  convertPresencePayload: function(roster) {
    if (roster.childNodes.length === 0) {
      return [];
    } else {
      var child = roster.childNodes[0];
      roster.removeChild(child);
      return [{
        uid: child.childNodes[0].nodeValue,
        presence: Number(child.getAttribute("presence"))
      }].concat(this.convertPresencePayload(roster))
    }
  }
},
  driver_convert_presence_payload:{
  convertPresencePayload: function(roster) {
    if (roster.childNodes.length === 0) {
      return [];
    } else {
      var child = roster.childNodes[0];
      roster.removeChild(child);
      return [{
        uid: child.childNodes[0].nodeValue,
        presence: Number(child.getAttribute("presence"))
      }].concat(this.convertPresencePayload(roster));
    }
  }
},
  json_utils:{

  buildJsonArgs: function(args, options) {
    options = options || {};

    options = Rtcc.merge(this, options);
    if (options.startDate) {
      args.push(options.startDate);
    } else {
      args.push("");
    }
    if (options.stopDate) {
      args.push(options.stopDate);
    } else {
      args.push("");
    }
    if (options.title) {
      args.push(options.title);
    } else {
      args.push('');
    }
    if (options.location) {
      args.push(options.location);
    } else {
      args.push("");
    }
    return args;

  }
},
  my_presence_validate_input:{
  validateInput: function(input) {
    var castedInput = Number(input);
    if (isNaN(castedInput)) {
      throw new Error("Presence value must be numeric");
    }
    if (castedInput > 255) {
      throw new Error("Presence value must be no greater than 255");
    }
    if (castedInput < 0) {
      throw new Error("Presence value cannot be negative");
    }
  }
},
  roster_xml_builder:{
  uidToXml: function(uid) {
    return '<uid>' + uid + '</uid>'
  },
  toXml: function(name, uid_array) {
    var str = "<" + name + ">";
    for (var i = 0; i < uid_array.length; i++) {
      str += this.uidToXml(uid_array[i]);
    }
    str += "</" + name + ">";
    return str;
  }
},
  webrtc_convert_chuncked_presence_payload:{
  convertChunkedPresenceArray: function(pre_proc_array) {
    var slice = pre_proc_array.splice(0, 2)
    if (slice.length > 0) {
      return [{
        uid: slice[1],
        presence: Number(slice[0])
      }].concat(this.convertChunkedPresenceArray(pre_proc_array));
    } else {
      return [];
    }
  }
},
  webrtc_convert_presence_payload:{
  convertPresencePayload: function(uid_array) {
    if (uid_array.length > 0) {
      return [{
        presence: Number(uid_array.shift()),
        uid: uid_array.shift()
      }].concat(this.convertPresencePayload(uid_array))
    } else {
      return [];
    }
  }
},
  xml_utils:{
  getKeyIfExists: function(node, key) {
    var tag = node.getElementsByTagName(key)[0]
    if (tag && tag.childNodes[0] && typeof tag.childNodes[0].nodeValue === 'string') {
      return tag.childNodes[0].nodeValue.decodeHTML();
    } else {
      return undefined;
    }
  },
  getChildrenIfExists: function(options, node, childName) {
    var found = node.getElementsByTagName(childName);
    if (found.length > 0 && found[0].childNodes[0] !== undefined)
      options[childName] = found[0].childNodes[0].nodeValue;

  },

  buildXmlArgs: function(options) {
    options = options || {};
    options = Rtcc.merge(this, options);
    var xml_message = "";
    if (options.startDate) {
      xml_message += "<startdate>" + options.startDate + "</startdate>";
    }

    if (options.stopDate) {
      xml_message += "<stopdate>" + options.stopDate + "</stopdate>";
    }

    if (options.title) {
      xml_message += "<title>" + options.title.encodeHTML() + "</title>";
    }

    if (options.location) {
      xml_message += "<location>" + options.location.encodeHTML() + "</location>";
    }
    return xml_message
  }
}};

  global_config = load_configs(arguments, {
    version: version,
    downloadUrl: downloadUrl,
    endpointUrl: endpointUrl,
    uiBaseUrl: '@@UI_URL@@',
    mode_parameter: mode
  });
  global_config = Rtcc.merge(global_config, system_info());
  global_config.instance = instance;
  debug("OS : " + global_config.os);
  debug("OS version : " + global_config.osVersion);
  debug("Is mobile : " + global_config.mobile);
  debug("Browser : " + global_config.browser);
  debug("Browser version : " + global_config.browserVersion);
  debug("JS version : " + global_config.version);
  debug("Screensize : " + global_config.screenSize);
  debug("Mode : " + modeMap[global_config.mode_parameter]);
  debug("---------------------------");

  var start_in_audio_only = false;
  this.requests = new RequestManager();
  this.responseManager = new ResponseManager();
  this.responseManager.handlers = response_handlers;

  /**
   * <b>RTCCdriver only</b>
   *
   * Generates a RTCCdriver stack dump for Rtcc Technical Support.
   * @return {void}
   */
  this.coredump = function() {
    this.requests.run('coredump');
  };

  /**
   * <b>RTCCdriver only</b>
   *
   * Returns the RTCCdriver download URL.
   *
   * @returns {string} URL to download the RTCCdriver.
   */
  this.getDownloadUrl = function() {
    return downloadUrl;
  };


  /**
   * When trying to join a conf call as an external user using the native Android/IOS SDKs.
   * In order for the native mobile application to know wich external user is associated with the web session, A suffix needs to be passed in the URL scheme.
   * This function is used to retrive said suffix.
   * @return {String} suffix associated with the current external user
   */
  this.getSuffix = function() {
    return getSuffix();
  }

  /**
   * @description <b>RTCCdriver and WebRTC</b>
   *
   * @returns {string} The RtccUserType given as a parameter of the Rtcc object
   */
  this.getRtccUserType = function(argument) {
    return global_config.rtccUserType;
  }

  /**
   * <b>RTCCdriver only</b>
   *
   * Returns the version of the RTCCdriver. You need to use the onGetHandler("version", obj) to catch the answer.
   *
   * @returns {string} The RTCCdriver version is sent as a property of the second parameter in the onGetHandler callback. For example:
   * onGetHandler('version', obj) with obj.value = RTCC_DRIVER_VERSION
   */
  this.getRtccDriverVersion = function() {
    this.requests.run('get_version');
  };


  this.getCurrentCall = function() {
      globalVars.call;
    }
    /**
     * <b>RTCCdriver only</b>
     *
     * Set the x,y pixel position of the top-left corner of the WeemoDriver UI.
     * This function should be called when you receive a "sipOk" message in the onConnectionHandler()
     * @param {string} value -   The argument is a string with the "x,y" coordinate value.
     *
     * @return {void}
     *
     * @example
     * rtcc.setCallWindowDefaultPosition("100,100")
     */
  this.setCallWindowDefaultPosition = function(value) {
    this.requests.run('set_call_window_default_position', [value]);
  };

  /**
   * <b>RTCCdriver only</b>
   *
   * <p>Retrieves the x,y pixel position of the RTCCdriver UI.<br />
   * The return data is passed to the <a href="#toc19">onGetHandler("callWindowDefaultPosition", obj)</a> callback.</p>
   *
   * @return {string} "callWindowDefaultPosition" as a first parameter in the onGetHandler callback. For instance: onGetHandler("domainstatus", obj).
   * @return {string} "value" The argument is a string with the "x,y" coordinate value. As a property of the second parameter in the onGetHandler callback. For instance: onGetHandler("domainstatus", obj) with obj.value = "50,50"
   */
  this.getCallWindowDefaultPosition = function() {
    this.requests.run('get_call_window_default_position');
  };

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * Sets the unique Token value to identify the session.
   *
   * @param {string} Value of the token to set.
   * @return {void}
   */
  this.setToken = function(value) {
    globalVars.token = value;
  };

  /**
   * @function
   * @description <b>RTCCdriver and WebRTC</b>
   *
   * Sets the Application Identifier (Application Identifier is provided by SightCall).
   *
   * @param {string} webApplicationIdentifier The Web Application Referer to set.
   * @return {void}
   */
  this.setAppId = function(value) {
    global_config.appId = value;
  };

  this.setWebAppId = this.setAppId;

  /**
   * @function
   * @description <b>RTCCdriver only</b>
   *
   * Sets the test mode.
   *
   * @param {boolean} enable - true to enable, false to disable.
   * @return {void}
   * @private
   */
  this.setTestMode = function(enable) {
    this.requests.run('set_test_mode', [enable]);
  };

  /**
   * @function
   * @description <b>RTCCdriver only</b>
   *
   * Sends the JS API version to the driver.
   *
   * @return {void}
   * @private
   */
  this.setJsApiVersionToDriver = function() {
    this.requests.run('set_js_api_version_to_driver', [global_config.version]);
  };


  /**
   * @function
   * @private
   * @description <b>RTCCdriver only</b>
   *
   * Sends an URL referer to the driver.
   *
   * @param {string} url - The URL to send
   * @return {void}
   */
  this.setUrlReferer = function(url) {
    this.requests.run('set_url_referer', [url]);
  };



  this.setWebAppId = this.setAppId;

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * Activates the console logs.
   *
   * @param {string} debugLevel
   * <table>
   * <thead><th>Value</th><th>Description</th></thead>
   * <tr><td>0</td><td>No debug messages</td></tr>
   * <tr><td>1</td><td>First level of debug messages</td></tr>
   * <tr><td>3</td><td>Detailed debug messages</td></tr>
   * </table>
   *
   * @return {void}
   */
  this.setDebugLevel = function(value) {
    global_config.debugLevel = value;
  };

  /**
    * <b>RTCCdriver and WebRTC</b>
    *
    * Sets the name of the user displayed in UI.<br />
    *
    * @param {string} displayName Value of the display name.
    * Must respect naming rules:
       <ul>
       <li> String – max 127 characters</li>
       <li> Not Null</li>
       <li> UTF-8 Characters except: ", ,' (single quote, double quote, space)</li>
       <li>Case sensitive</li>
       </ul>
    * @return {void}
  */
  this.setDisplayName = function(value) {
    global_config.displayName = value;
    this.requests.run('send_display_name', [value]);
  };

  /**
    * <b>RTCCdriver and WebRTC</b>
    *
    * Configures user type, internal or external to domain.
    *
    * @param {string} rtccUserType
    * <table class="fieldtable">
       <thead><th>Value</th><th>Description</th></thead>
       <tbody>
         <tr>
           <td>internal</td>
           <td>For authenticated users</td>
         </tr>
         <tr>
           <td>external</td>
           <td>For non-authenticated users</td>
         </tr>
       </tbody>
     </table>

    * @return {void}
    */
  this.setRtccUserType = function(value) {
    global_config.rtccUserType = value;
  };

  /*
   * <b>RTCCdriver and WebRTC</b>
   *
   * Allows to specify which platform is used.<br />
   * To be used upon Rtcc support request only.
   *
   * @param {string} platform This variable takes the token value of the platform ("prod/", "ppr/"). If you don't set a platform, the platform is set by default at "prod/"
   * @return {void}
   */
  this.setHap = function(value) {
    global_config.hap = value;
  };

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * Returns the value of the current Rtcc API version.
   *
   * @returns {string} Rtcc.js version.
   */
  this.getVersion = function() {
    return global_config.version;
  }; // Js version or wd version ?

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * Get the current user's display name.
   *
   * @returns {String} Value of the current user's display name.
   */
  this.getDisplayName = function() {
    return global_config.displayName;
  };


  this.getStatus = function(uidStatus) {
    this.requests.run('get_status', [uidStatus]);
  };

  /*
   * <b>RTCCdriver and WebRTC</b>
   *
   * Returns the token in use on your session.
   *
   * @returns {String} Value of the current user's token.
   */
  this.getToken = function() {
    return globalVars.token;
  };

  /*
   * <b>RTCCdriver and WebRTC</b>
   *
   * Returns the Application Identifier in use.
   *
   * @returns {String} Value of the Application Identifier in use.
   */
  this.getWebAppId = function() {
    return global_config.appId;
  };

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * <p>Launches the connection between real-time client and Javascript.</p>
   * <p>If the connection with the RTCCdriver or WebRTC succeeds, you should receive a notification in the onConnectionHandler callback to inform that you are correctly connected to a real-time client:
   * <ul>
   * <li>onConnectionHandler(<b><font class="paramname">"connectedRtccDriver"</font>)</b> OR onConnectionHandler(<b><font class="paramname">"connectedWebRTC"</font>)</b></li>
   * </ul> IIf you are not able to use webRTC and if the RTCCdriver was not started, the application receives a dedicated callback:
   * <ul>
   *   <li>onRtccDriverNotStarted(downloadUrl)</li>
   * </ul> This callback is used only if the RTCCdriver detection failed, you can have the download url in <font class="paramname"><b>"downloadUrl"</b></font> variable.
   * </p>
   * <p>Other possible callback messages during initialization phase:
   * <ul><li>onConnectionHandler(<font class="paramname"><b>"webRTCCapabilities"</b></font>)<br>
   *   Used when the Javascript API detects our WebRTC browser capability.</li>
   * </ul>
   * <ul>
   *   <li>onConnectionHandler(<font class="paramname"><b>"unsupportedOS"</b></font>)<br>
   *   Used when the Javascript API detects that your Operating System is not compatible with any RTCCdriver or WebRTC protocol.</li>
   * </ul>
   *   <ul>
   *   <li>Etc...</li>
   * </ul>
   * You can find the list of all the messages you can receive in the {@link Rtcc#onConnectionHandler}
   * </p>
   *
   * @return {void}
   */
  this.initialize = function(options) {
    actions.initialize(options);
  };


  /**
   * Set plugin to be embeded in the page, or to have its own seperate window.
   * @param {String} mode - An element of {@link Rtcc.pluginMode}
   */
  this.setPluginMode = function(mode) {
    this.requests.run('set_plugin_mode', [mode]);
  }

  /**
    * <b>RTCCdriver & WebRTC</b>
    * <p>
    * Can be called after receiving a message <font class="paramname"><b>"loggedasotheruser"</b></font> in the onConnectionHandler() callback in order to force the connection with a different user.</p>
     <p><b>Mechanism:</b><br/>
       If you are already connected to the RTCCdriver with user A and try to connect to the same RTCCdriver with user B, you receive a <font class="paramname"><b>"loggedasotheruser"</b></font> message in the onConnectionHandler() callback of user B. At this moment, if you want to disconnect user A and connect user B, you have to use the forceAuthenticate method.

       <ul><li> rtcc.forceAuthenticate();</ul>

       When user B uses the force authenticate, user A receives a <font class="paramname"><b>"dropped"</b></font> message in the onConnectionHandler() callback, to tell he was disconnected.
       <ul><li> onConnectionHandler(<font class="paramname"><b>"dropped"</b></font>)</li></ul>
     Once User B receives a <font class="paramname"><b>"sipOk"</b></font> message in the onConnectionHandler() callback, user B is ready to receive or create a call.
     </p>
     <p><b>Multiple Authenticate:</b><br/>
       If User A is already connected and begins another authentication with the same credentials (App Identifier &amp; Uid) but with a different display name, the new display name will be updated.
     </p>
    */
  this.forceAuthenticate = function() {
    globalVars.force_connect = true;
    actions.authenticate(global_config);
  };

  /**
   * @deprecated since version 5.2 use {@link Rtcc#forceAuthenticate forceAuthenticate} instead
   **/
  this.authenticate = function() {
    debug('WARNING: authenticate is depreciated, please use forceAuthenticate instead', {
      show_on_debug_level: 0
    });
    this.forceAuthenticate();
  };



  this.bypass = function() {
      this.requests.run('verify_user', ['bypass']);
    }
    /**
     * <b>RTCCdriver & WebRTC</b>
     * <p>Creates and initiates video call.</p>
     *   <dl class="params">
     *   <dt>1 to 1 call:</dt>
     *     <pre>rtcc.createCall(<font class="paramname">"CALLEE_UID"</font>, <font class="paramname">"internal"</font>, <font class="paramname">"CALLEE_DISPLAYNAME"</font>)</pre>
     *     Value of CALLEE_UID is the destination uid (the callee)<br>
     *     Value of type is "internal"<br>
     *     Value of CALLEE_DISPLAYNAME is the destination Display Name (the callee)
     * </dl>
     * <dl class="params">
     *   <dd>
     *       <b>UID</b> must respect naming rules:<br />
     *       <li> Min size = 6 characters;
     *       <li> Max size = 90 characters;
     *       <li> Authorized characters:  UTF8 - unicode - Latin basic, except: & " # \ % ?
     *       <li> Case sensitive, no space character.</li>
     *       <br />
     *       <b>Display Name</b> must respect naming rules:<br />
     *       <li> String – max 127 characters<br/>
     *       <li> Not Null<br/>
     *       <li> UTF-8 Characters execpt: " ' <br/>
     *   </dd>
     * </dl>

     *
     * @param {string} uidToCall This variable takes the uid value of the user to call.
     * @param {string} type This variable describes the type of call you are going to do
     * @param {string} displaynameToCall  This variable takes the displayed name value of the user to call.
     */
  this.createCall = function(uidToCall, type, displayNameToCall, is_audio_only) {
    var obj = {};
    obj.uidToCall = uidToCall;
    obj.type = type;
    start_in_audio_only = is_audio_only;
    obj.displayNameToCall = displayNameToCall;
    this.requests.run('create_call', [obj, is_audio_only]);
  };
  var start_in_audio_only = false;


  /**
   *<b>RTCCdriver and WebRTC</b>
   *
   * Creates a call thats starts in no video
   * @param {string} uidToCall This variable takes the uid value of the user to call.
   * @param {string} type  This variable describes the type of call you are going to do
   * @param {string} displaynameToCall This variable takes the displayed name value of the user to call.
   **/
  this.createCallNoVideo = function(uidToCall, type, displayNameToCall) {
    this.createCall(uidToCall, type, displayNameToCall, true)
  };

  /**
   * <b>RTCCdriver and WebRTC</b>
   * Send message to person with which you are in a call
   * @param {string} message to send
   * @deprecated
   **/
  this.sendInbandMessage = function(message) {
      debug("WARNING: sendInbandMessage is depreciated in favor of `call.sendInbandMessage`");
      if (globalVars.call) {
        globalVars.call.sendInbandMessage(message);
      }
    }
    /**
     * <b>RTCCdriver only</b>
     * Create a six digit code
     * @param {string} mode - An element of {@link Rtcc.sixDigitsType}
     * @param {string} displayname - display name of the external associated with this code
     * @param {string} meeting_point_id - in mode N_TO_N, the id of a previously created meeting point.
     */
  this.createSixDigits = function(mode_parameter, displayName, meeting_point_id) {
    this.requests.run('create_six_digits', [mode_parameter, displayName, meeting_point_id]);
  }

  /**
   * <b>RTCCdriver only</b>
   * Delete all six digits codes
   */
  this.deleteSixDigits = function() {
    this.requests.run('delete_six_digits');
  }

  this.setIceMode = function(mode_parameter) {
    this.requests.run('set_ice_mode', [mode_parameter]);
  };

  /** <b>RTCCdriver only</b>
   * Defines the quality of the video at the start of a call.
   * @param {String} profile - An element of {@link Rtcc.videoProfile}
   * @example
   * rtcc.setStartupProfile(Rtcc.videoProfile.SMALL)
   */

  this.setStartupProfile = function(profile) {
    this.requests.run('set_startup_profile', [profile]);
  }


  /**
   * <b> RTCCdriver Only</b>
   *
   * Defines the action associated with a click on either the video being broadcast or a screenshare
   * @param {String} pickup_mode An element of {@link Rtcc.pickupMode}
   * @example
   * rtcc.setPickupMode(Rtcc.pickupMode.NOVIDEO);
   **/
  this.setPickupMode = function(pickup_mode) {
    this.requests.run('set_pickup_mode', [pickup_mode]);
  }



  this.sendMessageToDriver = function(message) {
    modeFacade.send(message);
  }


  /**
   * <b>WebRTC only</b>
   * @return {Boolean} returns true if the chrome extention necesary for webrtc screen share is loaded
   */
  this.isShareExtensionLoaded = function() {
    return document.getElementById('rtcc-desktop-capture-installed') !== null
  }

  this.stop_reconnection_attempts = function() {
    global_config.stop_reconnection_attempts = true;
  }


  /**
   * <b> RTCCdriver only</b>
   *
   * Defines the size of the video box at the start of a call.
   * @param {String} startup_size - An element of {@link Rtcc.videoboxSize} (only Rtcc.videoboxSize.WIDE and Rtcc.videoboxSize.THUMB are supported)
   * @example
   * rtcc.setStartupSize(Rtcc.videoboxSize.WIDE)
   */
  this.setStartupSize = function(startup_size) {
    this.requests.run('set_startup_size', [startup_size]);
  }

  var createdMeetingPoints = {};

  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   *
   * Creates a meeting point.
   * @param {String} type - The type of conference you wish to create. can be "permanent" |  "scheduled"| "adhoc"
   * @param {Object} options
   * @param {int} [options.startDate] - Unix timestamp of begining of conference
   * @param {int} [options.stopDate] - Unix timestamp of end of conference
   * @param {String} [options.title] - Title of conference
   * @param {String} [options.location] - Where the conference will be held
   * @returns {MeetingPointHost}
   * status updates of the meeting point handeled via the onConfCallHandler callback
   */
  this.createMeetingPoint = function(conftype, options) {
    global_config.meetingPointBeingCreated = new MeetingPointHost(conftype, options);
    return global_config.meetingPointBeingCreated.create() ? global_config.meetingPointBeingCreated : false;
  }


  /**
   * <b>RTCC Driver Only</b>
   * gray out selected buttons when in call.
   * @param {Object} options
   * @param {Boolean} options.mute - true if mute button should be disabled
   * @param {Boolean} options.video - true if video button should be disabled
   * @param {Boolean} options.share - true if share button should be disabled
   **/
  this.setDisabledButtons = function(options) {
    this.requests.run('set_disabled_buttons', [options]);
  }

  /**
   * <b> RTCCdriver and WebRTC</b><br />
   *
   * Fetches a meeting point. The meeting point is passed as the second argument to the onConfCallHandler callback.
   * @param {int} meetingPointId The Id of the meeting point
   */

  this.getMeetingPoint = function(meetingPointId) {
    this.requests.run("get_meeting_point", [meetingPointId]);
  }

  var meetingPointAttendees = [];


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Tells the SightCall presence server the user status.
   * The result of the request is passed to the {@link Rtcc#onPresenceUpdate} callback.
   * @param {Integer} presenceInt - Integer between 0 and 255. 0 Means offline. The application determines the meaning for any other value.
   **/
  this.setMyPresence = function(presenceInt) {
    this.requests.run("set_my_presence", [presenceInt]);
  }


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Tells the SightCall acd server the agent status.
   * @param {String} hexString - 64 bit hex value in string format.
   **/
  this.setMyAcdStatus = function(hexString) {
    this.requests.run("set_my_acd_presence", [hexString]);
  }


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Gets the status of the whole roster registered via {@link Rtcc#rosterAdd}, see the {@link Rtcc#onRosterRetrieved} callback.
   **/
  this.getRoster = function() {
    this.requests.run("get_roster", []);
  }



  /**
   * <b> RTCCdriver, and WebRTC</b>
   *
   * Add uids to your presence roster. The result of the request is passed to the {@link Rtcc#onRosterUpdated} callback. Once you have added all the users to your contacts,
   * use {@link Rtcc#getRoster} to initialize their presence. You will receive their presence updates via {@link Rtcc#onPresenceUpdate}
   * @param {Array} uidArray - Array of uids to register on your roster
   **/
  this.rosterAdd = function(uid_array) {
    this.requests.run("roster_add", [uid_array, global_config]);
  }

  /**
   * <b> RTCCdriver and Plugin </b>
   * Show a notification bottom right of the screen
   * @param  {String} options.type an element of {@link Rtcc.toastType}
   * @param  {String} options.message message to display
   * @param  {String} options.from  from (required for Rtcc.toastType.MESSAGE)
   */
  this.toast = function(options) {
    this.requests.run('toast', [options]);
  }

  /**
   * <b> RTCCdriver and Plugin </b>
   * Clear notfifications created by {@link Rtcc#toast}
   */
  this.clearToasts = function() {
    this.requests.run('clear_toasts');
  }


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Get the presence of users not in current user roster. The result is passed to the {@link Rtcc#onBurstUpdate} callback.
   * @param {Array} uidArray - array of uids to remove from your roster
   **/
  this.getPresence = function(uid_array) {
    this.requests.run("get_presence", [uid_array, global_config]);
  }


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Remove  uids from your presence roster.  The result of the request is passed to the {@link Rtcc#onRosterUpdated} callback.
   * @param {Array} uidArray - array of uids to remove from your roster
   **/
  this.rosterRemove = function(uid_array) {
    this.requests.run("roster_remove", [uid_array, global_config]);
  }



  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   * Empty the roster. The result of the request is passed to the {@link Rtcc#onRosterUpdated} callback.
   **/

  this.rosterClear = function() {
    this.requests.run("roster_clear", []);
  }


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Joins a video meeting when attendee.
   * @param {String} meetingPointId - the id of the meeting point the attendee wishes to join
   * @returns {MeetingPointAttendee}
   **/
  this.joinConfCall = function(meetingPointId) {
    meetingPointAttendees[meetingPointId] = new MeetingPointAttendee(meetingPointId, "Conference");
    meetingPointAttendees[meetingPointId].request();
    return meetingPointAttendees[meetingPointId];
  }

  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   *
   * Sends a message via data channel.
   * @param {String} id - identifier of person we send message too, can either be a UID, or the originId recieved in the onDataChannelMessageReceived callback
   * @param {String} message - message to send.
   **/

  this.sendDataChannelMessage = function(id, message) {
    this.requests.run("send_data_channel_message", [id, message]);
  }

  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   *
   * Sends a message via skynet
   * @param {Integer} message_id - identifier of the message, set by sender application value can be  any whole number between 0 to 4294967296
   * @param {String} uid - uid of user to send too.
   * @param {String} message - message to send
   **/


  this.sendMessage = function(message_id, uid, message) {
    this.requests.run("send_message", [message_id, uid, message, global_config]);
  }


  /**
   * used in standalone mode. if webrtc compatible, registerSip will register to sip server. Once sipOk is received in the {@link Rtcc#onConnectionHandler}, {@link Rtcc#createCall} will become available.
   */
  this.registerSip = function(forceDriver) {
    global_config.standAlone = false;
    if (webrtc_compliant() && forceDriver !== true) {
      loadUi();
      this.requests.run('sip_register');
      return true;
    } else {
      webrtcFacade.websock.close();
      return false;
    }
  }

  /**
   * <b>Rtccdriver only</b>
   * Sets the threshold of autoerase feature in share mode. autoerase is disabled by default.
   * @param {Integer} threshold - Integer between 0 and 1000. 0 disables the feature. 1 is the most sesnsitive, 1000 is the least sensitive
   *
   * @private
   **/

  this.setAutoEraseThreshold = function(threshold) {
    this.requests.run('set_auto_erase_threshold', [threshold]);
  }

  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   *
   * Acknowledge receit of a data channel message
   * @param {Integer} message_id -  identifier of the message, set by sender application value can be  any whole number from 0 to 4294967296
   * @param {String} uid - uid of message sender
   * @param {Integer} status - current message status. value can be any wholenumber from 0 to 255
   **/
  this.acknowledgeMessage = function(message_id, uid, status) {
    this.requests.run("send_acknowledge", [message_id, uid, status, global_config]);
  }


  /**
   *
   * <b> RTCCdriver and WebRTC</b>
   *
   * Get the attendeeUrl of a uids permanent conference.
   * @private
   **/

  this.getPermanentMeetingPointByUid = function(uid) {
    this.requests.run('get_permanent_meeting_point_by_uid', [uid]);
  }

  this.test = {
    onPluginMessageCallback: pluginFacade.callback,

    setConfig: function(key, value) {
      global_config[key] = value;
    },
    getConfig: function(key) {
      if (global_config[key]) {
        return global_config[key];
      } else {
        debug("config not present");
        return false;
      }
    },
    set: function(key, value) {
      globalVars[key] = value;
    },
    get: function(key) {
      if (globalVars[key]) {
        return globalVars[key];
      } else {
        debug("variable " + key + " not present");
      }
    },
    inject: function(name, value) {
      eval(name + ' = value;');
    },
    eject: function(name) {
      return eval(name);
    }
  };


  /**
   * request an agent, to cancel request see {@link Rtcc#cancelAgentRequest} response handled via the {@link Rtcc#onCallDistributorQueueUpdate} and  the {@link Rtcc#onCallDistributorAgentAvailable}
   *
   * @param {AgentRequestEntity} agentRequestEntity - information about the type of agent the client is trying to retreive
   *
   **/
  this.requestAgent = function(agentRequestEntity) {
    this.requests.run('request_agent', [agentRequestEntity]);
  }

  /**
   *  <b> Rtcc Driver only </b>
   *  toggle video overlays (buttons, top banner)
   *  @param {Sring} mode - and element of {@link Rtcc.overlay}
   */
  this.setOverlay = function(mode) {
    this.requests.run('set_overlay', [mode]);
  }

  /**
   * request a list of agents, to cancel request see {@link Rtcc#cancelAgentRequest} response handled via the {@link Rtcc#onCallDistributorQueueUpdate} and  the {@link Rtcc#onCallDistributorAgentAvailable}
   *
   * @param {AgentRequestEntity} agentRequestEntity - information about the type of agent the client is trying to retreive
   *
   **/
  this.requestAgentList = function(agentRequestEntity) {
    this.requests.run('request_agent_list', [agentRequestEntity]);
  }

  /**
   * Cancel agent requests
   */

  this.cancelAgentRequest = function() {
    this.requests.run('cancel_agent_request');
  }

  /**
   * Gets the wait list for the current provider.  response handled via the {@link Rtcc#onWaitListRetrieved}
   **/
  this.getWaitList = function() {
    this.requests.run('get_wait_list');
  }

  /**
   * @return {string} An element of {@link Rtcc.connectionModes} representing the type of connection used.
   */
  this.getConnectionMode = function() {
    if (modeFacade && modeFacade.getConnectionMode)
      return modeFacade.getConnectionMode('');
  }

  /**
   * <b>RTCCdriver and WebRTC</b>
   *
   * Closes the connection and restarts the connection proceess. In RtccDriver mode, the driver is also restarted.
   *
   * @return {void}
   */

  this.reset = function() {
    this.requests.run("reset");
  };


  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Deletes a conference call.
   * @param {Number} meetingPointId = the id of the meeting point a host would like to delete.
   **/

  this.deleteMeetingPoint = function(meetingPointId) {
    return this.requests.run("delete_meeting_point", [meetingPointId]);
  }

  var currentMeetingPointDeletedId;


  this.updateWallSettings = function(options) {
    this.requests.run('update_wall_settings', [options])
  }

  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Disconnects from the cloud.
   */
  this.disconnect = function() {
    clearTimeout(timeoutid);
    if (modeFacade.websock) modeFacade.websock.close();
    globalVars.state = Rtcc.STATES.SIP_NOK;
  }

  this.getWallSettings = function() {
    this.requests.run('get_wall_settings');
  }



  /**
   * <b> RTCCdriver and WebRTC</b>
   *
   * Disconnects from the cloud and removes lingering timers inside the object. It is then possible to
   * dereference the variable containing the Rtcc object without any side-effect.
   * @return {undefined} undefined
   *
   * @example
   * //create a new Rtcc object
   * var a = new Rtcc(...);
   * //destroy the object and use the return value to set `a` to undefined.
   * a = a.destroy()
   */
  this.destroy = function() {
    if (modeFacade.websock) {
      modeFacade.websock.onmessage = function() {

      }
    }
    this.disconnect();
    globalVars.state = Rtcc.STATES.DESTROYED;

    objectForEach(globalVars.timeout, function(k, v) {
      clearTimeout(v);
    });
    apiEvents.off();
    apiEvents.offAll();
    if (modeFacade.removePlugin) modeFacade.removePlugin();
    debug('Rtcc object destroyed.')
  }


  var apiEvents = new Vent();
  bindObjectToVent(this, apiEvents)

  /**
   * Binds a callback to an event triggered by the API.
   * @function on
   * @memberof Rtcc
   * @instance
   *
   * @param {String|Array} event - The name of the event, or an array of event names
   * @param {Function} callback - The callback that will be invoked when the event triggers.
   * @param {Object} [context] - Context that will be passed to the callback, as the this keyword.
   *
   * @example
   * var rtccObject = new Rtcc(...);
   * //a function that will be used as a callback
   * function sipOk(){
   *   alert('Ready!');
   * }
   * //binds sipOk to then event 'cloud.sip.ok'
   * rtccObject.on('cloud.sip.ok', sipOk);
   * rtcc.initialize(); //will trigger the event and invoke the sipOk callback
   */

  /**
   * Binds a callback to all events triggered by the API.
   * @function onAll
   * @memberof Rtcc
   * @instance
   *
   * @param {Function} callback - The callback that will be invoked every time an event triggers.
   * @param {Object} [context] - Context that will be passed to the callback, as the this keyword.   *
   * A property eventName will be added to the context, containing the name of the event triggered, as a string.
   *
   * @example
   * var rtccObject = new Rtcc(...);
   * function tracer(){
   *   console.log(this.eventName)
   * }
   * rtccObject.onAll(tracer);
   * rtcc.initialize();
   */

  /**
   * Removes callbacks previously bound with {@link Rtcc#on}, filtered by event name, function and context.
   * A callback will be removed only if all arguments provided match how it was bound.
   * @function off
   * @memberof Rtcc
   * @instance
   *
   * @param {String|Array} event - The name of the event, or an array of event names
   * @param {Function} [callback] - If provided, only callbacks matching the function will be removed.
   * @param {Object} [context] - If provided, only callbacks with a matching context will be removed.
   *
   * @example
   * var rtccObject = new Rtcc(...);
   * function sipOk(){
   *   alert('Ready!');
   * }
   * //bind a callback twice
   * rtccObject.on('cloud.sip.ok', sipOk);
   * rtccObject.on('cloud.sip.ok', sipOk);
   * //unbind all callbacks on the event
   * rtccIbject.off('cloud.sip.ok')
   * rtcc.initialize();
   */

  /**
   * Removes callbacks previously bound with {@link Rtcc#onAll}, filtered by function and context.
   * A callback will be removed only if all arguments provided match how it was bound.
   * @function offAll
   * @memberof Rtcc
   * @instance
   *
   * @param {Function} [callback] - If provided, only callbacks matching the function will be removed.
   * @param {Object} [context] - If provided, only callbacks with a matching context will be removed.
   *
   * @example
   * var rtccObject = new Rtcc(...);
   * function tracer(){
   *   console.log(this.eventName)
   * }
   * //this will log all events during the connection
   * rtccObject.onAll(tracer);
   * rtcc.initialize();
   * //removes the tracer callback
   * rtcc.offAll(tracer)
   */

};


  window.Rtcc = Rtcc;
})(window);
;
Rtcc.merge = function() {
  var obj = {},
    i = 0,
    il = arguments.length,
    key;
  for (; i < il; i++) {
    for (key in arguments[i]) {
      if (arguments[i].hasOwnProperty(key)) {
        obj[key] = arguments[i][key];
      }
    }
  }
  return obj;
};
;
Rtcc._safelog = function(str) {
  if (window.console && window.console.log)
    window.console.log(str)
}
;
/* jshint ignore:start */

/*
 *  Copyright (c) 2014 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree.
 */

/* More information about these options at jshint.com/docs/options */
/* global mozRTCIceCandidate, mozRTCPeerConnection,
mozRTCSessionDescription, webkitRTCPeerConnection */
/* exported trace,requestUserMedia */

'use strict';

var RTCPeerConnection = null;
var getUserMedia = null;
var attachMediaStream = null;
var reattachMediaStream = null;
var webrtcDetectedBrowser = null;
var webrtcDetectedVersion = null;

function trace(text) {
  // This function is used for logging.
  if (text[text.length - 1] === '\n') {
    text = text.substring(0, text.length - 1);
  }
  if (window.performance) {
    var now = (window.performance.now() / 1000).toFixed(3);
    Rtcc._safelog(now + ': ' + text);
  } else {
    Rtcc._safelog(text);
  }
}

if (navigator.mozGetUserMedia) {
  Rtcc._safelog('This appears to be Firefox');

  webrtcDetectedBrowser = 'firefox';

  webrtcDetectedVersion =
    parseInt(navigator.userAgent.match(/Firefox\/([0-9]+)\./)[1], 10);

  // The RTCPeerConnection object.
  RTCPeerConnection = function(pcConfig, pcConstraints) {
    // .urls is not supported in FF yet.
    if (pcConfig && pcConfig.iceServers) {
      for (var i = 0; i < pcConfig.iceServers.length; i++) {
        if (pcConfig.iceServers[i].hasOwnProperty('urls')) {
          pcConfig.iceServers[i].url = pcConfig.iceServers[i].urls;
          delete pcConfig.iceServers[i].urls;
        }
      }
    }
    return new mozRTCPeerConnection(pcConfig, pcConstraints);
  };

  // The RTCSessionDescription object.
  window.RTCSessionDescription = mozRTCSessionDescription;

  // The RTCIceCandidate object.
  window.RTCIceCandidate = mozRTCIceCandidate;

  // getUserMedia shim (only difference is the prefix).
  // Code from Adam Barth.
  getUserMedia = navigator.mozGetUserMedia.bind(navigator);
  navigator.getUserMedia = getUserMedia;

  // Shim for MediaStreamTrack.getSources.
  MediaStreamTrack.getSources = function(successCb) {
    setTimeout(function() {
      var infos = [{
        kind: 'audio',
        id: 'default',
        label: '',
        facing: ''
      }, {
        kind: 'video',
        id: 'default',
        label: '',
        facing: ''
      }];
      successCb(infos);
    }, 0);
  };

  // Creates ICE server from the URL for FF.
  window.createIceServer = function(url, username, password) {
    var iceServer = null;
    var urlParts = url.split(':');
    if (urlParts[0].indexOf('stun') === 0) {
      // Create ICE server with STUN URL.
      iceServer = {
        'url': url
      };
    } else if (urlParts[0].indexOf('turn') === 0) {
      if (webrtcDetectedVersion < 27) {
        // Create iceServer with turn url.
        // Ignore the transport parameter from TURN url for FF version <=27.
        var turnUrlParts = url.split('?');
        // Return null for createIceServer if transport=tcp.
        if (turnUrlParts.length === 1 ||
          turnUrlParts[1].indexOf('transport=udp') === 0) {
          iceServer = {
            'url': turnUrlParts[0],
            'credential': password,
            'username': username
          };
        }
      } else {
        // FF 27 and above supports transport parameters in TURN url,
        // So passing in the full url to create iceServer.
        iceServer = {
          'url': url,
          'credential': password,
          'username': username
        };
      }
    }
    return iceServer;
  };

  window.createIceServers = function(urls, username, password) {
    var iceServers = [];
    // Use .url for FireFox.
    for (var i = 0; i < urls.length; i++) {
      var iceServer =
        window.createIceServer(urls[i], username, password);
      if (iceServer !== null) {
        iceServers.push(iceServer);
      }
    }
    return iceServers;
  };

  // Attach a media stream to an element.
  attachMediaStream = function(element, stream) {
    Rtcc._safelog('Attaching media stream');
    element.mozSrcObject = stream;
  };

  reattachMediaStream = function(to, from) {
    Rtcc._safelog('Reattaching media stream');
    to.mozSrcObject = from.mozSrcObject;
  };

} else if (navigator.webkitGetUserMedia) {
  Rtcc._safelog('This appears to be Chrome');

  webrtcDetectedBrowser = 'chrome';
  // Temporary fix until crbug/374263 is fixed.
  // Setting Chrome version to 999, if version is unavailable.
  var result = navigator.userAgent.match(/Chrom(e|ium)\/([0-9]+)\./);
  if (result !== null) {
    webrtcDetectedVersion = parseInt(result[2], 10);
  } else {
    webrtcDetectedVersion = 999;
  }

  // Creates iceServer from the url for Chrome M33 and earlier.
  window.createIceServer = function(url, username, password) {
    var iceServer = null;
    var urlParts = url.split(':');
    if (urlParts[0].indexOf('stun') === 0) {
      // Create iceServer with stun url.
      iceServer = {
        'url': url
      };
    } else if (urlParts[0].indexOf('turn') === 0) {
      // Chrome M28 & above uses below TURN format.
      iceServer = {
        'url': url,
        'credential': password,
        'username': username
      };
    }
    return iceServer;
  };

  // Creates an ICEServer object from multiple URLs.
  window.createIceServers = function(urls, username, password) {
    return {
      'urls': urls,
      'credential': password,
      'username': username
    };
  };

  // The RTCPeerConnection object.
  RTCPeerConnection = function(pcConfig, pcConstraints) {
    return new webkitRTCPeerConnection(pcConfig, pcConstraints);
  };

  // Get UserMedia (only difference is the prefix).
  // Code from Adam Barth.
  getUserMedia = navigator.webkitGetUserMedia.bind(navigator);
  navigator.getUserMedia = getUserMedia;

  // Attach a media stream to an element.
  attachMediaStream = function(element, stream) {
    if (typeof element.srcObject !== 'undefined') {
      element.srcObject = stream;
    } else if (typeof element.mozSrcObject !== 'undefined') {
      element.mozSrcObject = stream;
    } else if (typeof element.src !== 'undefined') {
      element.src = URL.createObjectURL(stream);
    } else {
      Rtcc._safelog('Error attaching stream to element.');
    }
  };

  reattachMediaStream = function(to, from) {
    to.src = from.src;
  };
} else {
  Rtcc._safelog('Browser does not appear to be WebRTC-capable');
}

// Returns the result of getUserMedia as a Promise.
function requestUserMedia(constraints) {
    return new Promise(function(resolve, reject) {
      var onSuccess = function(stream) {
        resolve(stream);
      };
      var onError = function(error) {
        reject(error);
      };

      try {
        getUserMedia(constraints, onSuccess, onError);
      } catch (e) {
        reject(e);
      }
    });
  }
  /* jshint ignore:end */
;
/**
 * <b>Rtcc Driver only</b>
 * @readonly
 * @enum {string}
 *
 **/
Rtcc.pickupMode = {
  /** When user clicks pickup button, call will be answered with video **/
  VIDEO: "video",
  /**  When user clicks pickup button, call will be answered with no video **/
  NOVIDEO: "novideo"
};


/**
 * Modes you can set for annotations on screenshare
 * @deprecated since 6.1
 * @see The bower package {@link https://github.com/sightcall/rtcc-integration}
 * @readonly
 * @enum {string}
 **/
Rtcc.annotationMode = {
  /** The mouse pointer will be displayed on the subject **/
  POINTER: "pointer",
  /** A right button mouse hold will draw at the current mouse position **/
  DRAW: "draw",
  /**  A right click will draw a circle around the point selected **/
  DROP: "drop"
};

/**
 * modes the plugin can be in
 * @readonly
 * @enum {string}
 */
Rtcc.pluginMode = {
  /** default mode the plugin is embeded on the page **/
  EMBEDDED: "embedded",
  /** the plugin instanciates its own seperate window  **/
  STANDALONE: "standalone"
}


/**
 * Sizes for the video box
 * @see {@link Rtcc#setStartupSize}
 * @see {@link RtccCall#setWindowSize}
 * @readonly
 * @enum {string}
 */
Rtcc.videoboxSize = {
  /**
   * 320*180
   * @default
   *
   */
  THUMB: "thumb",
  /** 640*360 */
  WIDE: "wide",
  FULLSCREEN: "fullscreen"
}


if (!Object.defineProperties) {
  Rtcc.videoboxStartupSize = Rtcc.videoboxSize;
} else {
  Object.defineProperties(Rtcc, {
    videoboxStartupSize: {
      get: function() {
        Rtcc._safelog('WARNING: videoboxStartupSize is depreciated, please use videoboxSize instead');
        return Rtcc.videoboxSize;
      }
    }
  });
}


/**
 * @readonly
 * @enum {string}
 */
Rtcc.callType = {
  /** for calls between two people  */
  ONE_TO_ONE: "1",
  /** for calls with N participants */
  N_TO_N: "n"
};




/**
 * @readonly
 * @enum {string}
 * @see {Rtcc#setOverlay}
 */
Rtcc.overlay = {
  /** default - all video overlay exist (buttons /title bar...) */
  ON: "1",
  /** show only video with no buttons */
  OFF: "0"
};


/**
 * @readonly
 * @enum {string}
 */
Rtcc.meetingPointMode = {
  /** No one can enter the conference anymore */
  LOCKED: "locked",
  /** The host does not have to accept new users */
  AUTO_ACCEPT: "auto-accept",
  /** The host needs to accept new users into the conference */
  DEFAULT: "default"
};


if (!Object.defineProperties) {
  Rtcc.meetingPointModes = Rtcc.meetingPointMode;
} else {
  Object.defineProperties(Rtcc, {
    meetingPointModes: {
      get: function() {
        Rtcc._safelog('WARNING: meetingPointModes is depreciated, please use meetingPointMode instead (with no "s").');
        return Rtcc.meetingPointMode;
      }
    }
  });
}


/**
 * A list of toastTypes
 * @enum {string}
 * @see {Rtcc#toast}
 */
Rtcc.toastType = {
    INFO: "info",
    MESSAGE: "message"
  }
  /**
   * A list of video definition profiles. All sizes are given in pixels.
   * @readonly
   * @enum {string}
   */
Rtcc.videoProfile = {
  /** 160*90 not supported by rtccdriver */
  THUMBNAIL: 'ld',
  /** 320*180 */
  SMALL: 'sd',
  /** 640*360 */
  MEDIUM: 'md',
  /** 1280*720 */
  HIGH: 'hd'
};


Rtcc.PRESENCE_STATES = {
  NOK: -1,
  OK: 1
};


/**
 * A list of connection modes
 * @readonly
 * @enum {string}
 */
Rtcc.connectionModes = {
  DRIVER: 'driver',
  PLUGIN: 'plugin',
  WEBRTC: 'webrtc'
}
;
Rtcc.STATES = {
  DESTROYED: -1,
  NOT_CONNECTED_TO_FACADE: 0,
  AUDIO_NOK: 1,
  SIP_NOK: 2,
  VERIFIED_USER_NOK: 3,
  CONNECTED_TO_FACADE: 4,
  VERIFIED_USER_OK: 5,
  SIP_OK: 6
};
;
/*
Global plugin loading function
It's global because the plugin can't call directly a given function
//TODO improve plugin to be able to call a given function
*/


var weemoPluginLoaded;

function onWeemoPluginLoaded() {
  weemoPluginLoaded = true;
}
