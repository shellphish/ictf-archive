var vm = require('vm')
var fs = require('fs')

function check(content) {
    try{vm.runInNewContext(content, {require:require,setTimeout:setTimeout})}
    catch(e) { return false}
    return true
}
module.exports = {
        calc: function calc(content) {
        var metadata = [content.length]
        metadata.toString=function(){s="";for(i=0;i<this.length;i++){s+=this[i];if(i!=this.length-1)s+=",";}return"["+s+"]"}
        return metadata
    },
    checkfile: function checkfile(fname) {
        if (!fs.existsSync("/var/ctf/curiosityblogging/posts/"+fname+".metadata")) {
            return false
        }
        var data = fs.readFileSync("/var/ctf/curiosityblogging/posts/"+fname+".metadata").toString().replace(/\s/,'')
        return check(data)
    }
}
