var glob = require('glob')
var shell = require('shelljs');
var fs = require('fs')
shell.exec('rm -rf commands.txt')
glob('/home/saad/Data/Twitter/Results/*.csv', function(er, files) {
    for (var i = 0; i < files.length; i++) {
        fl_nm = files[i].split('/home/saad/Data/Twitter/Results/')[1].split('_')[0]
        fs.appendFileSync('commands.txt', 'rsync --progress -r -u ' + files[i] + ' /home/saad/Data/Twitter/country/' + fl_nm + '/data/')
        fs.appendFileSync('commands.txt', '\n')
    }

   shell.exec('parallel -j 220 <commands.txt')
})