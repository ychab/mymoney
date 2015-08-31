var gulp = require('gulp');
var uglify = require('gulp-uglify');
var minifyCss = require('gulp-minify-css');
var concat = require('gulp-concat');

gulp.task('js', function () {
  return gulp.src([
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
    ])
    .pipe(concat('mymoney.min.js'))
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
