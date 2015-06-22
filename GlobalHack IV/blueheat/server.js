#!/bin/env node
//  OpenShift sample Node application
var express = require('express');
var fs      = require('fs');

var app = express();
app.set('view engine', 'jade'); 


/**
 *  Define the sample application.
 */
var SampleApp = function() {

    //  Scope.
    var self = this;


    /*  ================================================================  */
    /*  Helper functions.                                                 */
    /*  ================================================================  */

    /**
     *  Set up server IP address and port # using env variables/defaults.
     */
    self.setupVariables = function() {
        //  Set the environment variables we need.
        self.ipaddress = process.env.OPENSHIFT_NODEJS_IP;
        self.port      = process.env.OPENSHIFT_NODEJS_PORT || 8080;

        if (typeof self.ipaddress === "undefined") {
            //  Log errors on OpenShift but continue w/ 127.0.0.1 - this
            //  allows us to run/test the app locally.
            console.warn('No OPENSHIFT_NODEJS_IP var, using 127.0.0.1');
            self.ipaddress = "127.0.0.1";
        };
    };


    /**
     *  Populate the cache.
     */
    self.populateCache = function() {
        if (typeof self.zcache === "undefined") {
            self.zcache = { 'index.html': '' };
        }

        //  Local cache for static content.
        self.zcache['index.html'] = fs.readFileSync('./index.html');
    };


    /**
     *  Retrieve entry (content) from cache.
     *  @param {string} key  Key identifying content to retrieve from cache.
     */
    self.cache_get = function(key) { return self.zcache[key]; };


    /**
     *  terminator === the termination handler
     *  Terminate server on receipt of the specified signal.
     *  @param {string} sig  Signal to terminate on.
     */
    self.terminator = function(sig){
        if (typeof sig === "string") {
           console.log('%s: Received %s - terminating sample app ...',
                       Date(Date.now()), sig);
           process.exit(1);
        }
        console.log('%s: Node server stopped.', Date(Date.now()) );
    };


    /**
     *  Setup termination handlers (for exit and a list of signals).
     */
    self.setupTerminationHandlers = function(){
        //  Process on exit and signals.
        process.on('exit', function() { self.terminator(); });

        // Removed 'SIGPIPE' from the list - bugz 852598.
        ['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT',
         'SIGBUS', 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGTERM'
        ].forEach(function(element, index, array) {
            process.on(element, function() { self.terminator(element); });
        });
    };


    /*  ================================================================  */
    /*  App server functions (main app logic here).                       */
    /*  ================================================================  */

    /**
     *  Create the routing table entries + handlers for the application.
     */
    self.createRoutes = function() {
        self.routes = { };

        self.routes['/asciimo'] = function(req, res) {
            var link = "http://i.imgur.com/kmbjB.png";
            res.send("<html><body><img src='" + link + "'></body></html>");
        };

        self.routes['/'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.send(self.cache_get('index.html') );
        };

        self.routes['/blueheat'] = function(req, res) {
            res.send("<script type='text/javascript' src='gh_app_platform.js'></script><html><body><script>window.LD.request_height(455);</script><iframe frameBorder='0' scrolling='yes' height='450px' width='550' src='iframe'></iframe></body></html>");
        };

        self.routes['/iframe'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('iframe-content.html');
        };

        self.routes['/embed'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('embed.js');
        };

        self.routes['/scriptcam'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('scriptcam.js');
        };

        self.routes['/scriptcam.swf'] = function(req, res) {
            res.sendfile('scriptcam.swf');
        };

        self.routes['/5BDDBDFC.htm'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('5BDDBDFC.htm');
        };

        self.routes['/gh_app_platform.js'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('gh_app_platform.js');
        };

        self.routes['/dashboard'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('dashboard.html');
        };

        self.routes['/demo'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.sendfile('demo.html');
        };

        
         
    };


    /**
     *  Initialize the server (express) and create the routes and register
     *  the handlers.
     */
    self.initializeServer = function() {
        self.createRoutes();
        self.app = express.createServer();
        self.app.set('view engine', 'jade'); 

        //  Add handlers for the app (from the routes).
        for (var r in self.routes) {
            self.app.get(r, self.routes[r]);
        }
    };

    /**
     *  Initializes the sample application.
     */
    self.initialize = function() {
        self.setupVariables();
        self.populateCache();
        self.setupTerminationHandlers();

        // Create the express server and routes.
        self.initializeServer();
    };


    /**
     *  Start the server (starts up the sample application).
     */
    self.start = function() {
        //  Start the app on the specific interface (and port).
        self.app.listen(self.port, self.ipaddress, function() {
            console.log('%s: Node server started on %s:%d ...',
                        Date(Date.now() ), self.ipaddress, self.port);
        });
    };

    


};   /*  Sample Application.  */


/**
 *  main():  Main code.
 */
var zapp = new SampleApp();
zapp.initialize();
zapp.start();

