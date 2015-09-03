var gulp = require('gulp');
var uglify = require('gulp-uglify');
var minifyCss = require('gulp-minify-css');
var concat = require('gulp-concat');
var util = require('gulp-util');

gulp.task('js', function () {
  var map = [
    "./mymoney/static/bower_components/jquery/dist/jquery.js",
    "./mymoney/static/bower_components/bootstrap/dist/js/bootstrap.js",
    "./mymoney/static/bower_components/underscore/underscore.js",
    "./mymoney/static/bower_components/moment/moment.js",
    "./mymoney/static/bower_components/bootstrap-calendar/js/calendar.js",
    "./mymoney/static/bower_components/bootstrap-datepicker/dist/js/bootstrap-datepicker.js",
    "./mymoney/static/bower_components/chartjs/Chart.js",
    "./mymoney/core/static/core/js/core.js",
    "./mymoney/apps/banktransactionanalytics/static/banktransactionanalytics/banktransactionanalytics.js",
    "./mymoney/apps/banktransactions/static/banktransactions/banktransactions.js",
  ];
  var filename = 'mymoney.min.js';

  if (util.env.lang) {
    filename = 'mymoney.min.' + util.env.lang + '.js';

    if (util.env.lang_bt_cal) {
      map.push("./mymoney/static/bower_components/bootstrap-calendar/js/language/" + util.env.lang_bt_cal + ".js");
    }
    if (util.env.lang_bt_dp) {
      map.push("./mymoney/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker." + util.env.lang_bt_dp + ".js");
    }
  }

  return gulp.src(map)
    .pipe(concat(filename))
    .pipe(uglify())
    .pipe(gulp.dest('./mymoney/static/dist/js/'));
});

gulp.task('css', function () {
  return gulp.src([
      "./mymoney/static/mymoney/css/styles.css",
    ])
    .pipe(concat('mymoney.min.css'))
    .pipe(minifyCss())
    .pipe(gulp.dest('./mymoney/static/dist/css/'));
});

gulp.task('default', ['js', 'css']);
