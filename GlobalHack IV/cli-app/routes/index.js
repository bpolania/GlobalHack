var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
	color = req.query.color;
	res.render('index', { title: color });
});

module.exports = router;
