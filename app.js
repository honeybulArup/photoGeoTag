var express             = require('express'),
    path                = require('path');
    bodyParser          = require('body-parser');
    mongoose            = require('mongoose');
    expressSanitizer    = require('express-sanitizer');
    methodOverride      = require('method-override');

var index = require('./routes/index');
var app = express();

app.use(expressSanitizer());
app.use(methodOverride("_method"));

app.use(express.static(__dirname + '/public'));
app.set('views', path.join(__dirname, "views"))
app.set("view engine", 'ejs');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.get('/', function(req, res){
    res.render('index');
});

app.listen(3000, function() {
    console.log('Example App Listening on PORT:3000');
});