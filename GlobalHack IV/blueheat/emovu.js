#!/bin/env node

var fs      = require('fs');
var unirest = require('unirest');

unirest.post("http://api.emovu.com/api/video")
.header("X-Mashape-Key", "T85Som8eaBmshe8p4sWIfM4K0jfkp14k9TVjsnSP7T5UL8gOgu")
.header("LicenseKey", "54112511127281194042332873441465611588116310510731181056932213421607311541")
.field("computeAgeGroup", true)
.field("computeEmotions", true)
.attach("videoFile", fs.createReadStream("video.mp4"))
.end(function (result) {
  console.log(result.status, result.headers, result.body);
});